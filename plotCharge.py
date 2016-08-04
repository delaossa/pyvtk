from __future__ import print_function
import h5py
import numpy as np
import vtk

hf = h5py.File('charge-beam-driver-000026.h5','r')

data = hf.get('charge')
print('Shape of the array charge: ', data.shape,'\nType: ',data.dtype,'\n')

npdata = np.array(data)

# Changing to positive numbers (particle density)
npdata = -1 * npdata

# This is very slow
#for i in range(0, data.shape[0]):
#    for j in range(0, data.shape[1]):
#        for k in range(0, data.shape[2]):
#            npdata[i,j,k] = -npdata[i,j,k]

minvalue = np.amin(npdata)
maxvalue = np.amax(npdata)

print('Min value = ',minvalue)
print('Max value = ',maxvalue)

# For VTK to be able to use the data, it must be stored as a VTK-image.
# This can be done by the vtkImageImport-class which
# imports raw data and stores it.
dataImporter = vtk.vtkImageImport()

# The array is converted to a string of chars and imported.
data_string = npdata.tostring()
dataImporter.CopyImportVoidPointer(data_string, len(data_string))

# The type of the newly imported data is set to float.
dataImporter.SetDataScalarTypeToFloat()
# Because the data that is imported only contains an intensity value,
# the importer must be told this is the case.
dataImporter.SetNumberOfScalarComponents(1)
# The following two functions describe how the data is stored
# and the dimensions of the array it is stored in.
dataImporter.SetDataExtent(0, npdata.shape[0], 0, npdata.shape[1], 0, npdata.shape[2])
dataImporter.SetWholeExtent(0, npdata.shape[0], 0, npdata.shape[1], 0, npdata.shape[2])

alphaChannelFunc = vtk.vtkPiecewiseFunction()
alphaChannelFunc.AddPoint(0.0, 0.0)
alphaChannelFunc.AddPoint(1.1, 0.075)
alphaChannelFunc.AddPoint(1.6, 0.8375)
alphaChannelFunc.AddPoint(maxvalue, 1.0)

# This class stores color data and can create color tables from a few color points.
# to be of the colors red green and blue.
colorFunc = vtk.vtkColorTransferFunction()
colorFunc.AddRGBPoint(0.0, 0.705, 0.0156, 0.149)
colorFunc.AddRGBPoint(1.0, 0.865, 0.865, 0.865)
colorFunc.AddRGBPoint(maxvalue, 0.2313, 0.298, 0.753)

# The previous two classes stored properties.
# Because we want to apply these properties to the volume we want to render,
# we have to store them in a class that stores volume prpoperties.
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorFunc)
volumeProperty.SetScalarOpacity(alphaChannelFunc)
#volumeProperty.ShadeOn()
#volumeProperty.SetInterpolationTypeToLinear()

# We can finally create our volume.
# We also have to specify the data for it, as well as how the data will be rendered.
volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
#volumeMapper.SetBlendModeToMaximumIntensity();
#volumeMapper.SetSampleDistance(0.1)
#volumeMapper.SetAutoAdjustSampleDistances(0)
volumeMapper.SetInputConnection(dataImporter.GetOutputPort())

# The class vtkVolume is used to pair the previously declared volume as well as the properties to be used when rendering that volume.
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

# With almost everything else ready, its time to initialize the renderer and window
renderer = vtk.vtkRenderer()
renderWin = vtk.vtkRenderWindow()
renderWin.AddRenderer(renderer)
renderInteractor = vtk.vtkRenderWindowInteractor()
renderInteractor.SetRenderWindow(renderWin)

# We add the volume to the renderer ...
renderer.AddVolume(volume)

# ... set background color 
nc = vtk.vtkNamedColors()
renderer.SetBackground(nc.GetColor3d('MidnightBlue'))
# ... and set window size.
renderWin.SetSize(800, 600)

renderInteractor.Initialize()
renderInteractor.Start()
