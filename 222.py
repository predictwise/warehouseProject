__author__ = 'zcq'
#coding:utf-8

import zipfile, os, time, collada, shutil
from lxml.etree import XMLParser
from lxml import etree as ET
from collada import *


def readZipModel(kmzfile, name):
    print 'name: ', name
    unzipFile = zipfile.ZipFile(kmzfile) #解压kmz文件
    fileLists = unzipFile.namelist() #解压之后的文件列表

    postfix = ['dae', 'jpg', 'png'] #后缀
    mesh = None
    texturespath = '/home/wlw/oliverProjects/warehouseProject/app/static/img/'+name
    os.mkdir(texturespath)
    for each_file in fileLists:
        if each_file[-3:] in postfix[0]:
            daeFile = unzipFile.extract(unzipFile.getinfo(each_file))
            mesh = Collada(daeFile)

        if each_file[-3:] in (postfix[1] or postfix[2]):
            texture = unzipFile.extract(unzipFile.getinfo(each_file))
            #复制纹理到纹理文件夹
            shutil.copy(texture, texturespath)

    outpath = '/home/wlw/oliverProjects/warehouseProject/app/static/x3d/'+name+'.x3d'
    #先为要写入的x3d内容创建一个空文件
    os.mknod(outpath)

    flag = 1
    #一个大的模型由多个几何模型构成
    print 'geometries num: ', len(mesh.geometries)
    start = time.clock()

    for boundgeom in mesh.scene.objects('geometry'):
        polygones = []
        boundprimType = ''
        image = ''
        diffuseColor = ''
        tc = 0

        for boundprim in boundgeom.primitives():
            boundprimList = list(boundprim)

            if isinstance(boundprim, collada.triangleset.BoundTriangleSet):
                boundprimType = 'boundtriangleset'

            elif isinstance(boundprim, collada.lineset.BoundLineSet):
                boundprimType = 'boundlineset'

            for i in range(len(boundprimList)):
                polygones.append(boundprim.vertex[boundprim.vertex_index][i])

            for j, triOrline in enumerate(get_trianglesOrlines(boundprim, boundprimType)):
                if len(triOrline.material.effect.params) != 0:
                    surface, sampler = triOrline.material.effect.params
                    image_file = surface.image.path
                    #print 'image_file: ', image_file
                    imagelist = image_file.split('/')
                    image = imagelist[1]
                    #print 'image: ', image
                    tc = 1

                else:
                    diffuseColor = ''
                    colortuple = triOrline.material.effect.diffuse
                    for color in colortuple[0:3]:
                        diffuseColor = diffuseColor + str(color) + ' '
                    tc = 2

        each_coordIndex, each_point = polyToIdxfaceset(polygones)
        genePartX3D(each_coordIndex, each_point, image, diffuseColor, boundprimType, outpath, name, flag, tc)
        flag = flag + 1

    total = time.clock() - start
    print 'time: ', total


def get_trianglesOrlines(boundprim, boundprimType):
    if boundprimType == 'boundtriangleset':
        for triangle in boundprim.triangles():
            #type(triangle)  <class 'collada.triangleset.Triangle'>
            yield triangle
    elif boundprimType == 'boundlineset':
        for line in boundprim.lines():
            #type(line)  <class 'collada.lineset.Line'>
            yield line


def polyToIdxfaceset(polygones):
    coordIndex = '' #索引
    point = '' #坐标值
    k = 0 #索引号
    #获取每一个二维列表
    for polygone in polygones:
        #获取每一个二维列表中每一个一维列表
        for poly in polygone:
            #获取每一个坐标值(x,y,z),即每一个顶点的坐标值
            for c in poly:
                point = point + str(c) + ' '
            coordIndex = coordIndex + str(k) + ' '
            k = k + 1
        #'-1'代表这个多边形面,或者一条线段结束
        coordIndex = coordIndex + '-1 '

    return coordIndex, point


def genePartX3D(coordIndex, point, image, diffuseColor, boundprimType, outpath, name, flag, tc):

    #print 'primitiveType: ', primitiveType
    #判断是否第一次调用此函数
    if flag == 1:
        tree = ET.parse('base.x3d')
    else:
        tree = ET.parse(outpath)

    root = tree.getroot()
    group = root.find('.//Group')
    shape = ET.SubElement(group, 'Shape')
    apr = ET.SubElement(shape, 'Appearance')

    #tc为1,代表只有纹理贴图
    #tc为2,代表只有颜色
    if tc == 1:
        imagetex = ET.SubElement(apr, 'ImageTexture')
        image = '/static/img/'+name+'/'+image
        imagetex.set('url', image)
        imagetex.set('repeatS', 'true')
        imagetex.set('repeatT', 'true')
        #print image
    elif tc == 2:
        #print 'diffuseColor: ', diffuseColor
        matr = ET.SubElement(apr, 'Material')
        matr.set('diffuseColor', diffuseColor)

    if boundprimType == 'boundtriangleset':
        ifs = ET.SubElement(shape, 'IndexedFaceSet')
        ifs.set('DEF', 'building'+str(flag))
        ifs.set('coordIndex', coordIndex)
        ifs.set('solid', 'true')
        coord = ET.SubElement(ifs, 'Coordinate')
        coord.set('point', point)
    elif boundprimType == 'boundlineset':
        ils = ET.SubElement(shape, 'IndexedLineSet')
        ils.set('DEF', 'building'+str(flag))
        ils.set('coordIndex', coordIndex)
        ils.set('solid', 'true')
        coord = ET.SubElement(ils, 'Coordinate')
        coord.set('point', point)

    tree.write(outpath)


if __name__ == '__main__':
    kmzdir = '/home/wlw/wh3d/wh3d_kmzs/'
    kmzfiles = os.listdir(kmzdir)
    for kmzfile in kmzfiles:
        name = kmzfile[:-4]
        kmzfile = kmzdir + kmzfile
        readZipModel(kmzfile, name)



