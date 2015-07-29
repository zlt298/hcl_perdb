import simplekml
import matplotlib as mpl
import matplotlib.pyplot as plt
from math import sqrt

def plotGoogleColorMap(title,coords,vals,names):
    """
    Takes inputs:
        title -string for the resulting file name(without .kml extension)
        coords -list of tuples containing (longitude,latitude) as floats
        vals -list of float or integer values that are associated with the coordinates of the same index
        names -list of string names associated with the coordinates of the same index
        
    The function will output a .kml file (to be opened in Google Earth) in the current working directory with the name: title+'.kml'
    vals would be normalized and fit to a color scale from 1 at dark red to white at 0.5 and dark blue at 0
    
    The output is in relative scale for the dataset passed in. Visual scaling is done by calculating the longest distance between two coordinates
    and using that value to scale the height and cross section of the columns.
    """
    maxHeightScale = 20000 #picked to visual scale
    maxWidthScale = lambda x:0.00356*(x*x)+0.0028*x #curve fitted to visual scale for japan and hawaii
    
    def findDiameter(points):
        diam = 0
        for i,j in ((k,l) for k in points for l in points if k<>l):
            d = sqrt(abs(i[0]-j[0])**2 + abs(i[1]-j[1])**2)
            if d > diam: diam = d
        return diam if diam != 0 else 1
    
    kml = simplekml.Kml()

    min_,max_ = min(vals),max(vals)
    Range = max_-min_
    vals = [[int(i * 255) for i in mpl.cm.RdBu_r((j-min_)/float(Range))[:3]]+[(j-min_)/float(Range)] for j in vals]

    diam = findDiameter(coords)
    print diam
    
    for ind,coord in enumerate(coords):
        x,y = coord
        delta = maxWidthScale(diam)
        
        h = vals[ind][3]*maxHeightScale*diam
        pol = kml.newpolygon(name=names[ind],extrude = 1,tessellate=1,altitudemode = 'absolute')
        pol.outerboundaryis = [(x+delta,y,h), (x,y+delta,h),(x-delta,y,h),(x,y-delta,h),(x+delta,y,h)]
        pol.style.polystyle.color = simplekml.Color.changealphaint(255, simplekml.Color.rgb(*vals[ind][:3]))
        pol.style.linestyle.color = simplekml.Color.rgb(*vals[ind][:3])

        pnt = kml.newpoint(name=names[ind])
        pnt.coords = [coord]
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
        pnt.style.iconstyle.scale = 0.2
        pnt.style.labelstyle.scale = 0.5
    
    kml.save(title + ".kml")
