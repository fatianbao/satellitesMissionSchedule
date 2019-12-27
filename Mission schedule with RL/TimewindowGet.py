

import math
import datetime
import numpy as np
import pymap3d as pm
import numpy as np

def GSAT():

    import pandas as pd  # 导入pandas包
    Orbitdata = pd.read_csv("TWORbitdata.csv")
    time=Orbitdata['Time']#取a列
    x=Orbitdata['x (km)']
    y=Orbitdata['y (km)']
    z=Orbitdata['z (km)']
    vx=Orbitdata['vx (km/sec)']
    vy=Orbitdata['vy (km/sec)']
    vz=Orbitdata['vz (km/sec)']

    # for i in reader:
    #     x.append(i[0])
    #     y.append(i[1])
    #     z.append(i[2])
    #     time.append(i[0])
    #     print(i[0])
    sensor_angle=15 #degree
    Longitude_3=100
    Latitude_3=30
    # MAX_ElevationAngle=45
    Altitude =0
    # HPOP_Results = joblib.load('TWOrbitdata.pkl')


    # Start_Time = joblib.load('Start_Time.pkl')

    year = 2016
    month = 5
    day = 2
    hour = 6
    minute = 0
    second = 0

    # t_start_jd = Julian_date(year, month, day, hour, minute, second)

    # MJD_UTC_Start = t_start_jd - 2400000.5
    max_elev=0
    max_t=0
    datetime.datetime(year, month, day, hour, minute, second)
    for t in time:
        # print('t',t)
        t_datetime=datetime.datetime(year, month, day, hour+t//3600, (minute+t//60)%60, (second +t)%60)
        # print('t_datetime',t_datetime)
        az, elev, slantRange=pm.eci2aer((x[t]*1e3, y[t]*1e3, z[t]*1e3), Latitude_3, Longitude_3, Altitude, t_datetime,useastropy=False)
        # print('elev',elev)
        # print('az', az)
        if elev> max_elev:

            max_elev=elev

            max_t=t

        else:

            pass
    print('max_t',max_t-18*60-40,'max_elev',max_elev)
    # max_t=max_t+1
    x_max = x[max_t]*1e3
    y_max = y[max_t]*1e3
    z_max = z[max_t]*1e3
    t_max_datetime = datetime.datetime(year, month, day, hour + max_t // 3600, (minute + max_t // 60) % 60, (second + max_t) % 60)
    # print(' t_max_datetime ', t_max_datetime )
    x_max_ecef,y_max_ecef,z_max_ecef=pm.eci2ecef(np.array((x_max,y_max,z_max)),t_max_datetime,useastropy= False)
    x_target_3, y_target_3, z_target_3 = pm.geodetic2ecef(Latitude_3, Longitude_3, Altitude,deg=True)
    x_target_sat_3=x_max_ecef-x_target_3
    y_target_sat_3=y_max_ecef-y_target_3
    z_target_sat_3=z_max_ecef-z_target_3
    index1=x_max_ecef*x_target_sat_3+y_max_ecef*y_target_sat_3+z_max_ecef*z_target_sat_3

    index2=math.sqrt(x_max_ecef**2+y_max_ecef**2+z_max_ecef**2)*math.sqrt(x_target_sat_3**2+y_target_sat_3**2+z_target_sat_3**2)
    # print('Index',index1,index2)
    v_direction = np.array([vx[max_t]*1e3, vy[max_t]*1e3, vz[max_t]*1e3])
    r_direction = np.array([x_max, y_max, z_max])
    key_vector=np.cross(v_direction, r_direction)
    key_vector_ecef= pm.eci2ecef(np.array((key_vector[0], key_vector[1], key_vector[2])), t_max_datetime, useastropy=False)
    target_sat_ecef=np.array((x_target_sat_3,y_target_sat_3,z_target_sat_3))
    if np.dot(key_vector_ecef,target_sat_ecef) <0:

        symbol= -1

    else:

        symbol=1
    # print(symbol)
    alpha=symbol*abs(math.degrees(math.acos(index1/index2)))
    print('alpha', alpha)
        # x, y, z = pm.geodetic2ecef(Latitude_3, Longitude_3, Altitude)
        # r_ICRF = get_ground_station_postion_ICRF(t, Latitude_3, Longitude_3, Altitude, MJD_UTC_Start)

    TimeWindow=[]

    for t in time:

        t_datetime = datetime.datetime(year, month, day, hour + t // 3600, (minute + t // 60) % 60, (second + t) % 60)
        x_ecef, y_ecef, z_ecef = pm.eci2ecef(np.array((x[t]*1e3, y[t]*1e3, z[t]*1e3)),t_datetime,useastropy=False)
        v_direction = np.array([vx[t] * 1e3, vy[t] * 1e3, vz[t] * 1e3])
        r_direction = np.array([x[t]* 1e3, y[t]* 1e3, z[t]* 1e3])
        key_vector = np.cross(v_direction, r_direction)
        key_vector_ecef = pm.eci2ecef(np.array((key_vector[0], key_vector[1], key_vector[2])), t_datetime,
                                      useastropy=False)
        # x_target_sat_3 = x_ecef - x_target_3
        # y_target_sat_3 = x_ecef - y_target_3
        # z_target_sat_3 = x_ecef - z_target_3
        # target_sat_ecef = np.array((x_target_sat_3, y_target_sat_3, z_target_sat_3))

        r_direction_toEC_unit = -r_direction / math.sqrt(r_direction[0] ** 2 + r_direction[1] ** 2 + r_direction[2] ** 2)
        key_vector_unit = key_vector / math.sqrt(key_vector[0] ** 2 + key_vector[1] ** 2 + key_vector[2] ** 2)
        alpha_abs = abs(alpha)
        if symbol == -1:

            opt_axis = r_direction_toEC_unit * math.tan(math.radians(alpha_abs)) + key_vector_unit

        else:
            opt_axis = r_direction_toEC_unit * math.tan(math.radians(alpha_abs)) - key_vector_unit

        opt_axis_ecef = pm.eci2ecef(opt_axis, t_datetime,useastropy=False)


        x_sat_target_3 = -x_target_sat_3
        y_sat_target_3 = -x_target_sat_3
        z_sat_target_3 = -z_target_sat_3
        index1 = opt_axis_ecef[0]  * x_sat_target_3 + opt_axis_ecef[1]  * y_sat_target_3 + opt_axis_ecef [2] * z_sat_target_3

        index2 = math.sqrt(opt_axis_ecef[0] ** 2 + opt_axis_ecef[1] ** 2 + opt_axis_ecef[2]  ** 2) * math.sqrt(
            x_sat_target_3 ** 2 + y_sat_target_3 ** 2 + z_sat_target_3 ** 2)

        theta = math.degrees(math.acos(index1 / index2))
        print('theta',theta)

        if theta <= sensor_angle:

            TimeWindow.append(t-18*60-40)

        else:

            pass
    print('Timewindow',TimeWindow)
# def test():
#
#
#     # print('1')



if __name__ == "__main__":

    GSAT()
