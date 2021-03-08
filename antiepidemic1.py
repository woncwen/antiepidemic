## Generate experimental data and solve the model
## 2021-02-14
## woncwen

# import openpyxl
import numpy as np
import xlwt
from numpy import random
import pandas as pd


def get_dis(loc):    # Get the distance between the supply and demand side through coordinates
    n = len(loc)
    dis = np.zeros(shape=(n,n))
    for i in range(n):
        for j in range(n):
                dis[i][j] = np.sqrt(sum(np.power(loc[i]-loc[j],2)))  # Calculating geographic distance by European distance,eq.4
    print('dis: \r\n',dis)
    return dis

def get_sdr(sd):       # Generate the supply-demand vector w and calculate the supply-demand ratio Delta,eq.1-2
    [n, m] = sd.shape
    sdr = np.zeros(shape=(n,n))
    tem = np.zeros(shape=(n,n,m))
    for i in range(n):
        for j in range(n):
            for k in range(m):
                if sd[i][k] * sd[j][k] < 0:
                    if sd[i][k] > 0:
                        tem[i][j][k] = -sd[i][k]/sd[j][k]
                    else:
                        tem[i][j][k] = 0
                else:
                    tem[i][j][k] = 0
    for i in range(n):
        for j in range(n):
            sdr[i][j] = sum(tem[i][j])
    print('sdr:\n',sdr)
    return sdr

def get_consist(sd):            # Calculate the consistency of supply and demand,eq.3
    [n,m] = sd.shape
    sim = np.zeros(shape=(n,n))
    for i in range(n):
        for j in range(n):
            fz = 0
            fm1 = 0
            fm2 = 0
            for k in range(m):
                if sd[i][k]*sd[j][k] < 0:
#                     sim[i][j] = sum(-sd[i]*sd[j])/(np.sqrt(sum(sd[i]*sd[i]))*np.sqrt(sum(sd[j]*sd[j])))
                    fz += -sd[i][k]*sd[j][k]
                    fm1 += sd[i][k]*sd[i][k]
                    fm2 += sd[j][k]*sd[j][k]
                else:
                    fz += 0
                    fm1 += 0
                    fm2 += 0
            if fm1 * fm2 != 0:
                sim[i][j] = fz/(np.sqrt(fm1) * np.sqrt(fm2))
            else:
                sim[i][j] = 0
    print('sim:\r\n',sim)
    return sim

def get_coe(loc, sd, t):     # Calculating the coefficient matrix of objective function C, eq.6
    [n,m] = sd.shape
    dis = get_dis(loc)
    sdr = get_sdr(sd)
    sim = get_consist(sd)
    coe = np.zeros(shape=(n,n))   
    for i in range(n):
        for j in range(n):
            if dis[i][j] != 0:
                coe[i][j] = sdr[i][j]*sim[i][j]/ dis[i][j]
            else:
                coe[i][j] = 0
    print('coe'+ str(t)+':\r\n',coe)
    s2n = np.zeros(shape = (n,n,m))
    for k in range(m):
        for i in range(n):
            for j in range(n):
                if sd[i][k] > 0 and sd[j][k] < 0:
                    if abs(sd[i][k]) >= abs(sd[j][k]):
                        s2n[i][j][k] = abs(sd[j][k])
                    else:
                        s2n[i][j][k] = abs(sd[i][k])
                else:
                    s2n[i][j][k] = 0
    sn1 = s2n[0]  # The available quantity of each subject to other subjects
    sn2 = s2n[1]
    sn3 = s2n[2]
    sn4 = s2n[3]
    sn5 = s2n[4]
    sn6 = s2n[5]
    file_name = str(t) + 'coe2155.xls'
    Data =xlwt.Workbook() # Create workbooks and output experimental process data in XSL format
    sheet1 = Data.add_sheet(u'sd',cell_overwrite_ok=True) # supply and demand data
    [h,l]=sd.shape
    for i in range (h):
        for j in range (l):
            sheet1.write(i,j,str(sd[i,j]))
    sheet2 = Data.add_sheet(u'sn1',cell_overwrite_ok=True) # Available quantity of a1
    [h,l]=sn1.shape
    for i in range (h):
        for j in range (l):
            sheet2.write(i,j,str(sn1[i,j]))
    sheet3 = Data.add_sheet(u'sn2',cell_overwrite_ok=True) # Available quantity of a2
    [h,l]=sn2.shape
    for i in range (h):
        for j in range (l):
            sheet3.write(i,j,str(sn2[i,j]))
    sheet4 = Data.add_sheet(u'sn3',cell_overwrite_ok=True) # Available quantity of a3
    [h,l]=sn3.shape
    for i in range (h):
        for j in range (l):
            sheet4.write(i,j,str(sn3[i,j]))
    sheet5 = Data.add_sheet(u'sn4',cell_overwrite_ok=True) # Available quantity of a4
    [h,l]=sn4.shape
    for i in range (h):
        for j in range (l):
            sheet5.write(i,j,str(sn4[i,j]))
    sheet6 = Data.add_sheet(u'sn5',cell_overwrite_ok=True) # Available quantity of a5
    [h,l]=sn5.shape
    for i in range (h):
        for j in range (l):
            sheet6.write(i,j,str(sn5[i,j]))
    sheet7 = Data.add_sheet(u'sn6',cell_overwrite_ok=True) # Available quantity of a6
    [h,l]=sn6.shape
    for i in range (h):
        for j in range (l):
            sheet7.write(i,j,str(sn6[i,j]))
    sheet8 = Data.add_sheet(u'coe',cell_overwrite_ok=True) #创建sheet，地理距离矩阵
    [h,l]=coe.shape
    for i in range (h):
        for j in range (l):
            sheet8.write(i,j,str(coe[i,j]))
            Data.save(file_name)   
    return coe

def get_df_data(filename,header):         # Get the dataframe data in the CSV file
    data =  pd.read_csv(filename, header = header, encoding = 'utf-8')
    dfd = np.array(data)
    data_name = filename.replace('.csv','')
    print(data_name + ':\n',dfd)
    return dfd

def get_nsd(sn,sov,coe,t):  # Calculate the final supply and demand and allocation quantity,algorithm 1
    [m,n] = sn.shape
    sn2 = np.zeros(shape = (m,n))
    for i in range(m):
        for j in range(n):
            sn2[i][j] = sn[i][j]           
    sup = np.zeros(shape = (m,m,n))
    for i in range(m):
        sc = sov[i]*coe[i]
        for j in range(m):
            if sc[j] > 0 and max(sc) == sc[j]:     # sc[i][j] > 0 ，则 sn[i][k] > 0
                sc[j] = 0
                for k in range(n):
                    if sn[i][k] * sn[j][k] < 0:
                        if sn[i][k] > 0:
                            if abs(sn[i][k]) > abs(sn[j][k]):
                                sn[i][k] = sn[i][k] + sn[j][k]   
                                sup[i][j][k] = abs(sn[j][k])
                                sn[j][k] = 0
                            else:
                                sn[j][k] = sn[i][k] + sn[j][k]
                                sup[i][j][k] = sn[i][k]
                                sn[i][k] = 0
                        else:
                            sn[i][k] = sn[i][k]
                            sup[i][j][k] = 0
                    else:
                        sn[i][k] = sn[i][k]
                        sn[j][k] = sn[j][k]
                        sup[i][j][k] = 0
    sc2 = np.zeros(shape = (m,m))
    sup2 = np.zeros(shape = (m,m,n))
    sc2 = sov*coe
    print("sc2:\n", sc2)
    
    for l in range(m*m):
        x = 0
        for i in range(m):
            for j in range(m):
                x = np.max(sc2)
                if sc2[i][j] > 0 and x == sc2[i][j]:                
                    sc2[i][j] = 0
                    for k in range(n):
                        if sn2[i][k] > 0:
                            if sn2[i][k] * sn2[j][k] < 0:
                                if abs(sn2[i][k]) > abs(sn2[j][k]):
                                    sn2[i][k] = sn2[i][k] + sn2[j][k]
                                    sup2[i][j][k] = abs(sn2[j][k])
                                    sn2[j][k] = 0
                                else:
                                    sn2[j][k] = sn2[i][k] + sn2[j][k]
                                    sup2[i][j][k] = sn2[i][k]
                                    sn2[i][k] = 0
                            else:
                                sn2[i][k] = sn2[i][k]
                                sn2[j][k] = sn2[j][k]
                                sup2[i][j][k] = 0
                        else:
                            sn2[i][k] = sn2[i][k]
                            sn2[j][k] = sn2[j][k]
                            sup2[i][j][k] = 0

    sun = []
    for i in range(m):
        for j in range(m):
            if sov[i][j] == 1:
                sun.append([i+1,j+1] + list(sup[i][j]))
    sun = np.array(sun)    
    nsn = sn
    sun2 = []
    for i in range(m):
        for j in range(m):
            if sov[i][j] == 1:
                sun2.append([i+1,j+1] + list(sup2[i][j]))
    sun2 = np.array(sun2)
    nsn2 = sn2
    file_name = str(t) + 'nsd2155.xls'
    Data =xlwt.Workbook() 
    sheet1 = Data.add_sheet(u'nsn2',cell_overwrite_ok=True) # Final supply and demand
    [h,l]=nsn2.shape
    for i in range (h):
        for j in range (l):
            sheet1.write(i,j,str(nsn2[i,j]))
    sheet2 = Data.add_sheet(u'sun2',cell_overwrite_ok=True) # Supply quantity in supply schema
    [h,l]=sun2.shape
    for i in range (h):
        for j in range (l):
            sheet2.write(i,j,str(sun2[i,j]))
            Data.save(file_name) 
    return [nsn2, sun2]

if __name__ == "__main__":    
    n = 6  # Number of epidemic prevention subjects
    m = 7   # Types of anti-epidemic resources
    loc = random.uniform(1, 10, size=(n,2))  # Spatial coordinates of epidemic prevention subjects
    print('loc:\r\n',loc)
    pos = pd.DataFrame(loc)
    pos.to_csv(r"pos2155.csv", encoding = "utf-8", index = False) 
    
    sd = random.randint(-40,40,size=(n,m))   # Supply and demand of six epidemic prevention subjects
    print('sd:\r\n',sd)
    coe = get_coe(loc, sd, 1)
    its = int(input("Cycle execution times:"))
    for i in range(2,its+2):
        theta_name = 'theta' + str(i-1) + '.csv'
        flags = input("prepare theta"+ str(i-1) + ":")
        theta = get_df_data(theta_name, None)
        if theta.any():
            [nsd, sun] = get_nsd(sd, theta, coe, i)
            sd = nsd
            coe = get_coe(loc, sd, i)
        else:
            print("The solution is finished")
            break