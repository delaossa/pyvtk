from __future__ import print_function
import h5py
import numpy as np
from vtk import *


hfl = []
hfl.append(h5py.File('data/charge-He-electrons-000026.h5','r'))
hfl.append(h5py.File('data/charge-beam-driver-000026.h5','r'))
hfl.append(h5py.File('data/charge-plasma-000026.h5','r'))

window = vtk.vtkRenderWindow()
# ... and set window size.
window.SetSize(1280, 800)

renderer = vtk.vtkRenderer()
# Set background  
renderer.SetBackground(0,0,0)
# renderer.TexturedBackgroundOn()
# Other colors 
# nc = vtk.vtkNamedColors()
# renderer.SetBackground(nc.GetColor3d('MidnightBlue'))

data = []
npdata = []
npdatauchar = []
dataImport = []
volume = []
mapper = []
for i, hf in enumerate(hfl):
    data.append(hf.get('charge'))
    axisz = hf.get('AXIS/AXIS1')
    axisy = hf.get('AXIS/AXIS2')
    axisx = hf.get('AXIS/AXIS3')

    dz = (axisz[1]-axisz[0])/data[i].shape[2]
    dy = (axisy[1]-axisy[0])/data[i].shape[1]
    dx = (axisx[1]-axisx[0])/data[i].shape[0]

    print('\nFilename : ',hf.filename)
    print('Axis z range: [%.2f,%.2f]  Nbins = %i  dz = %.4f' % (axisz[0],axisz[1],data[i].shape[2],dz) )
    print('Axis x range: [%.2f,%.2f]  Nbins = %i  dx = %.4f' % (axisx[0],axisx[1],data[i].shape[0],dx) )
    print('Axis y range: [%.2f,%.2f]  Nbins = %i  dy = %.4f' % (axisy[0],axisy[1],data[i].shape[1],dy) )


    # Changing to positive integer types (particle density)
    # it is required by vtkVolumeRayCastMapper
    npdata.append(np.array(np.absolute(data[i])))
    minvalue = np.amin(npdata[i])
    maxvalue = np.amax(npdata[i])
    print('Minimum value = %.2f  Maximum = %.2f' % (minvalue,maxvalue))

    # Rescale data
    den1 = 255.0/maxvalue
    if "He-electrons" in hf.filename:
        den1 *= 100
    elif "plasma" in hf.filename:
        den1 *= 50

    npdata[i] = np.round(den1 * npdata[i])
        
    npdatauchar.append(np.array(npdata[i], dtype=np.uint8))
    print('Shape of the array: ', npdatauchar[i].shape,' Type: ',npdatauchar[i].dtype)
    minvalue = np.amin(npdatauchar[i])
    maxvalue = np.amax(npdatauchar[i])
    print('Minimum value = %.2f  Maximum = %.2f' % (minvalue,maxvalue))
    
    # For VTK to be able to use the data, it must be stored as a VTK-image.
    # This can be done by the vtkImageImport which
    # imports raw data and stores it.
    dataImport.append(vtk.vtkImageImport())

    # The array is converted to a string of chars and imported.
    #data_string = npdatauchar[i].tostring()
    #dataImport[i].CopyImportVoidPointer(data_string, len(data_string))
    dataImport[i].SetImportVoidPointer(npdatauchar[i])

    # The type of the newly imported data is set to float.
    dataImport[i].SetDataScalarTypeToUnsignedChar()
    # dataImport[i].SetDataScalarTypeToFloat()
    # Because the data that is imported only contains an intensity value,
    # the importer must be told this is the case.
    dataImport[i].SetNumberOfScalarComponents(1)
    # The following two functions describe how the data is stored
    # and the dimensions of the array it is stored in.
    dataImport[i].SetDataExtent(0, npdatauchar[i].shape[2]-1, 0, npdatauchar[i].shape[1]-1, 0, npdatauchar[i].shape[0]-1)
    dataImport[i].SetWholeExtent(0, npdatauchar[i].shape[2]-1, 0, npdatauchar[i].shape[1]-1, 0, npdatauchar[i].shape[0]-1)
    dataImport[i].SetDataSpacing(dz,dy,dx)
    dataImport[i].SetDataOrigin(0.0,axisy[0],axisx[0])
    
    dataImport[i].Update()
    
    # Opacity and color scales
    opacity = vtk.vtkPiecewiseFunction()
    color = vtk.vtkColorTransferFunction()
    if "plasma" in hf.filename:
        opacity.AddPoint(0, 0.0)
        opacity.AddPoint(den1, 0.01)
        opacity.AddPoint(10*den1, 0.8)
        opacity.AddPoint(maxvalue, 1.0)

        color.AddRGBPoint(0, 0.078, 0.078, 0.078)
        color.AddRGBPoint(den1, 0.188, 0.247, 0.294)
        color.AddRGBPoint(maxvalue, 1.0, 1.0, 1.0)
        # other palette
        #color.AddRGBPoint(0.0, 0.865, 0.865, 0.865)
        #color.AddRGBPoint(den1, 0.2313, 0.298, 0.753)
        #color.AddRGBPoint(maxvalue, 1.0, 1.0, 1.0)
    elif "beam" in hf.filename :
        opacity.AddPoint(0, 0.0)
        opacity.AddPoint(maxvalue, 1.0)

        color.AddRGBPoint(0.0, 0.220, 0.039, 0.235)
        color.AddRGBPoint(0.2*maxvalue, 0.390, 0.050, 0.330)
        color.AddRGBPoint(0.4*maxvalue, 0.700, 0.200, 0.300)
        color.AddRGBPoint(1.0*maxvalue, 1.000, 1.000, 0.200)
    elif "He-electrons" in hf.filename:
        opacity.AddPoint(0.0, 0.0)
        opacity.AddPoint(1, 0.1)
        opacity.AddPoint(100, 0.8)
        opacity.AddPoint(255, 1.0)

        color.AddRGBPoint(0.0, 0.220, 0.039, 0.235)
        color.AddRGBPoint(0.01*maxvalue, 0.627, 0.125, 0.235)
        color.AddRGBPoint(0.10*maxvalue, 0.700, 0.200, 0.300)
        color.AddRGBPoint(1.00*maxvalue, 1.000, 1.000, 0.200)


    volumeprop = vtk.vtkVolumeProperty()
    volumeprop.SetColor(color)
    volumeprop.SetScalarOpacity(opacity)
    volumeprop.ShadeOff()
    #volumeprop.ShadeOn()
    volumeprop.SetInterpolationTypeToLinear()

    #
    #compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
    #mapper = vtk.vtkVolumeRayCastMapper()
    #mapper.SetVolumeRayCastFunction(compositeFunction)

    #
    #mapper = vtkFixedPointVolumeRayCastMapper()
    #mapper = vtk.vtkVolumeTextureMapper2D()
    mapper.append(vtk.vtkGPUVolumeRayCastMapper())

    #mapper[i].SetBlendModeToMaximumIntensity();
    #mapper[i].SetSampleDistance(0.1)
    #mapper[i].SetAutoAdjustSampleDistances(0)
    
    # Add data to the mapper
    mapper[i].SetInputConnection(dataImport[i].GetOutputPort())

    # The class vtkVolume is used to pair the previously declared volume
    # as well as the properties to be used when rendering that volume.
    volume.append(vtk.vtkVolume())
    volume[i].SetMapper(mapper[i])
    volume[i].SetProperty(volumeprop)

    # Add the volume to the renderer ...
    renderer.AddVolume(volume[i])

    if (1) & ( ("beam" in hf.filename) | ("He-electrons" in hf.filename)):
        threshold = vtk.vtkImageThreshold()
        threshold.SetInputConnection(dataImport[i].GetOutputPort())
        threshold.ThresholdBetween(110,200)
        threshold.ReplaceInOn()
        threshold.SetInValue(100)  # set all values in range to 1
        threshold.ReplaceOutOn()
        threshold.SetOutValue(0)  # set all values out range to 0
        threshold.Update()

        dmc = vtk.vtkDiscreteMarchingCubes()
        dmc.SetInputConnection(threshold.GetOutputPort())
        #dmc.SetInputConnection(dataImport[i].GetOutputPort())
        dmc.GenerateValues(1, 100, 100)
        dmc.Update()

        mapper2 = vtk.vtkPolyDataMapper()
        mapper2.SetInputConnection(dmc.GetOutputPort())
        mapper2.SetLookupTable(color)
        mapper2.SetColorModeToMapScalars()
         
        actor = vtk.vtkActor()
        actor.SetMapper(mapper2)
        actor.GetProperty().SetOpacity(0.8)

        renderer.AddActor(actor)

    
window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
#style = vtkInteractorStyleTrackballCamera();
#interactor.SetInteractorStyle(style);

window.Render()
interactor.Initialize()
interactor.Start()
