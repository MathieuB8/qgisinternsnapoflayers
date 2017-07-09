from qgis.core import *
import copy
from PyQt4.QtCore import *
 
 
selectedpointscoord = []
allotherpointscoord = []
layer = qgis.utils.iface.activeLayer()

if  layer.selectedFeatureCount(): #continue script seulement si une couche est selectionne
    for feat in layer.selectedFeatures():
         geom= feat.geometry()
         attr =feat.attributes()
         polygon = geom.asPolygon()
         n=len(polygon[0])
         geomselected=polygon
         selectedpointscoord.append(polygon[0])
    for feat2 in layer.getFeatures():
             geom= feat2.geometry()
             attr =feat2.attributes()
             temp=geom.asPolygon()[0]
             if geom.asPolygon() != geomselected:
                del temp[0]
                allotherpointscoord.append(temp)
    del selectedpointscoord[0][0]    
    listptsinterdit=[] #point a deja ete snap ne pas comparer encore comme ca on touchera meme pas

    for z in range(len(selectedpointscoord[0])): # on snap les points de la couche selectionne un par un donc une boucle egal un point a snap
        focus = selectedpointscoord[0][z]
        distpoints=[]
        for k in range(len(allotherpointscoord)): #parcourt toutes les sous couches
            for i in range(len(allotherpointscoord[k])): #parcourt tous les points dune couche
                templist = []
                xa = focus[0]
                ya = focus[1]
                xb = allotherpointscoord[k][i][0]
                yb = allotherpointscoord[k][i][1]
                dist = ((xa-xb)**2 + (ya-yb)**2)**0.5
                distpoints.append(dist)
        #recherche du min
        min=distpoints[0]
        for bcl in range(len(distpoints)): # fonction min manuel car il faut ignorer les points au fur et a mesure ceux qui ont deja ete modifie
            if min >= distpoints[bcl] and not(bcl in listptsinterdit):
                min=distpoints[bcl]
                minindex = bcl
                mindist = distpoints[bcl]
            else:
                pass
        listptsinterdit.append(minindex)
        modifiedlist=allotherpointscoord
        indexleft=minindex
        for i in range(len(modifiedlist)): # modifie les coordonnes
            if indexleft<= len(modifiedlist[i]):
                modifiedlist[i][indexleft].setX(focus[0])
                modifiedlist[i][indexleft].setY(focus[1])
                break
            indexleft = indexleft - len(modifiedlist[i])


#creation des couches
    layer =  QgsVectorLayer('Polygon?crs=IGNF:LAMBE', 'poly' , "memory")
    layer.startEditing()
    pr = layer.dataProvider() 
    poly = QgsFeature()
    pr.addAttributes([QgsField("id", QVariant.Int)])

#creation des couches autre que celle selectionner
    for k in range(len(modifiedlist)):
        layer.startEditing()
        pts=[]
        for i in range(len(modifiedlist[k])):
             pts.append(QgsPoint(modifiedlist[k][i][0],modifiedlist[k][i][1]))
        res = QgsFeature()
        poly.setGeometry(QgsGeometry.fromPolygon([pts]))
        poly.setAttributes([k])
        pr.addFeatures([poly])       
        layer.commitChanges()   
        layer.updateExtents()
        
        
#creation de la couche selectionne en plus
    layer.startEditing()
    pts=[]
    for i in range(len(selectedpointscoord[0])):
         pts.append(QgsPoint(selectedpointscoord[0][i][0],selectedpointscoord[0][i][1]))
    res = QgsFeature()
    poly.setGeometry(QgsGeometry.fromPolygon([pts]))
    poly.setAttributes([k+1])
    pr.addFeatures([poly])       
    layer.commitChanges()   
    layer.updateExtents()


    layer.updateExtents()
    QgsMapLayerRegistry.instance().addMapLayers([layer])
else:
    print "Veuillez selectionner une couche en utilisant outil de selection et la selectionner dans longlet couches"
