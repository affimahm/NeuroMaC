####################################################################################
#
#    NeuroMaC: Neuronal Morphologies & Circuits
#    Copyright (C) 2013-2017 Okinawa Institute of Science and Technology Graduate
#    University, Japan.
#
#    See the file AUTHORS for details.
#    This file is part of NeuroMaC.
#
#    NeuroMaC is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3,
#    as published by the Free Software Foundation.
#
#    NeuroMaC is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

import timeit
import sys,time
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
import random
import sqlite3
import copy
import numpy
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import configparser

timer = time.time

def plot_with_radii() :    
    cfg_file = sys.argv[1]
    db_name = sys.argv[2]
    parser = configparser.ConfigParser()
    parser.read(cfg_file)
    colors= ['r','g','b','c','m','k']
    markers = [".","o","s","^","p","*"]
    c_mapping = {}
    m_mapping = {}

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("select distinct name from swc_data order by name")
    rets = cursor.fetchall()
    names =[]
    c=0
    for entity in rets :
        print ("entity: %s with color %s" % (str(entity[0]),colors[c%len(colors)]))
        names.append(entity[0])
        c_mapping[str(entity[0])] = colors[c%len(colors)]
        c = c + 1

    times = []
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    xmin,ymin,zmin = 0.0, 0.0, 0.0 
    dim_xyz = eval(parser.get("substrate","dim_xyz"))
    xmax = dim_xyz[0]
    ymax = dim_xyz[1]
    zmax = dim_xyz[2]
    ax.set_xlim([xmin,xmax])
    ax.set_ylim([ymin,ymax])
    ax.set_zlim([zmin,zmax])    
    for name in names :
        cursor.execute("select * from swc_data where name=? order by id",(str(name),) )
        rets = cursor.fetchall()

        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        soma = rets[0]
        soma_x = soma[3]
        soma_y = soma[4]
        soma_z = soma[5]
        radius = soma[9]
        x = soma_x + (radius * np.outer(np.cos(u), np.sin(v)))
        y = soma_y+(radius * np.outer(np.sin(u), np.sin(v)))
        z = soma_z+ (radius * np.outer(np.ones(np.size(u)), np.cos(v)))
        ax.plot_surface(x, y, z,rstride=2, cstride=2, color=c_mapping[name],linewidth=0, antialiased=False, shade=False)
        i = 0
        points = []
        print ('plotting: ', name)
        for entity in rets :
            # from_point = np.array([entity[2],entity[3],entity[4]])
            # to_point = np.array([entity[5],entity[6],entity[7]])
            radius = entity[9]
            t0 = timer()
            plt.plot([entity[3],entity[6]],\
                     [entity[4],entity[7]],\
                     [entity[5],entity[8]],\
                     linewidth=radius,\
                     color=c_mapping[name] )
            t1 =timer()
            times.append(t1-t0)
    t0 = timer()
    if db_name.startswith(".."):
        out_name = db_name.split("/")[-1].split(".")[0]+"_radii.pdf"
    else: 
        out_name = db_name.split(".")[0]+"_radii.pdf"    
    plt.savefig(out_name)
    t1 = timer()
    print ("writing the figure took: %fs" % (t1-t0))
    times.append(t1-t0)
    return np.sum(times)

if __name__=="__main__" :
    cfg_file = sys.argv[1]
    db_name = sys.argv[2]
    tt = plot_with_radii()
    print ('total time for radii: ', tt)
