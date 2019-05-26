# -*- coding: utf8 -*-
#!/usr/bin/python
#
# This was originaly derived from a cadquery script for generating PDIP models in X3D format
# from https://bitbucket.org/hyOzd/freecad-macros
# author hyOzd
#
# Adapted by easyw for step and vrlm export
# See https://github.com/easyw/kicad-3d-models-in-freecad

## requirements
## cadquery FreeCAD plugin
##   https://github.com/jmwright/cadquery-freecad-module

## to run the script just do: freecad scriptName modelName
## e.g. FreeCAD export_conn_jst_xh.py all

## the script will generate STEP and VRML parametric models
## to be used with kicad StepUp script

#* These are FreeCAD & cadquery tools                                       *
#* to export generated models in STEP & VRML format.                        *
#*                                                                          *
#* cadquery script for generating JST-XH models in STEP AP214               *
#*   Copyright (c) 2016                                                     *
#* Rene Poeschl https://github.com/poeschlr                                 *
#* All trademarks within this guide belong to their legitimate owners.      *
#*                                                                          *
#*   This program is free software; you can redistribute it and/or modify   *
#*   it under the terms of the GNU General Public License (GPL)             *
#*   as published by the Free Software Foundation; either version 2 of      *
#*   the License, or (at your option) any later version.                    *
#*   for detail see the LICENCE text file.                                  *
#*                                                                          *
#*   This program is distributed in the hope that it will be useful,        *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
#*   GNU Library General Public License for more details.                   *
#*                                                                          *
#*   You should have received a copy of the GNU Library General Public      *
#*   License along with this program; if not, write to the Free Software    *
#*   Foundation, Inc.,                                                      *
#*   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA           *
#*                                                                          *
#****************************************************************************

__title__ = "generator for wuert smt mounting hardware with inner through holes"
__author__ = "scripts: maurice and hyOzd; models: poeschlr"
__Comment__ = '''This generates step/wrl files for the official kicad library.'''

___ver___ = "1.0 26/05/2019"

class LICENCE_Info():
    ############################################################################
    STR_licAuthor = "Rene Poeschl"
    STR_licEmail = "poeschlr@gmail.com"
    STR_licOrgSys = ""
    STR_licPreProc = ""

    LIST_license = ["",]
    ############################################################################


save_memory = True #reducing memory consuming for all generation params
check_Model = True
stop_on_first_error = True
check_log_file = 'check-log.md'
global_3dpath = '../_3Dmodels/'


import sys, os
import traceback
from datetime import datetime

def generate(id, od, od1, h1, h):

    body = cq.Workplane("XY").circle(od/2).extrude(h)
    body = body.faces("<Z").workplane().circle(od1/2).extrude(h1)
    body = body.faces("<Z").workplane().circle(id/2).cutBlind(-h-h1)
    return body

# opend from within freecad
if "module" in __name__:
    import cadquery as cq
    from Helpers import show

    body = generate(
        id=2.25,
        od=4.35,
        od1=2.8,
        h1=1.4,
        h=3)
    show(body)

if __name__ == "__main__" or __name__ == "wuerth_smt_inside_through":
    sys.path.append("../_tools")
    import exportPartToVRML as expVRML
    import shaderColors
    import add_license as L

    import yaml

    if FreeCAD.GuiUp:
        from PySide import QtCore, QtGui

    try:
        # Gui.SendMsgToActiveView("Run")
    #    from Gui.Command import *
        Gui.activateWorkbench("CadQueryWorkbench")
        import cadquery as cq
        from Helpers import show
        # CadQuery Gui
    except Exception as e: # catch *all* exceptions
        print(e)
        msg = "missing CadQuery 0.3.0 or later Module!\r\n\r\n"
        msg += "https://github.com/jmwright/cadquery-freecad-module/wiki\n"
        if QtGui is not None:
            reply = QtGui.QMessageBox.information(None,"Info ...",msg)

    #######################################################################

    #from Gui.Command import *

    # Import cad_tools
    #sys.path.append("../_tools")
    from cqToolsExceptions import *
    import cq_cad_tools
    # Reload tools
    reload(cq_cad_tools)
    # Explicitly load all needed functions
    from cq_cad_tools import multiFuseObjs_wColors, GetListOfObjects, restore_Main_Tools, \
     exportSTEP, close_CQ_Example, saveFCdoc, z_RotateObject,\
     runGeometryCheck

    # Gui.SendMsgToActiveView("Run")
    #Gui.activateWorkbench("CadQueryWorkbench")
    #import FreeCADGui as Gui

    try:
        close_CQ_Example(App, Gui)
    except:
        FreeCAD.Console.PrintMessage("can't close example.")

    #import FreeCAD, Draft, FreeCADGui
    import ImportGui

    print(" ------------- Hello -------------- ")

    #######################################################################

    def export_one_part(params, mpn, log):
        print('\n##########################################################')

        if LICENCE_Info.LIST_license[0]=="":
            LIST_license=L.LIST_int_license
            LIST_license.append("")
        else:
            LIST_license=LICENCE_Info.LIST_license

        LIST_license[0] = "Copyright (C) "+datetime.now().strftime("%Y")+", " + LICENCE_Info.STR_licAuthor

        fp_params = params['footprint']
        mech_params = params['mechanical']
        part_params = params['parts'][mpn]

        size = str(mech_params['id'])
        if 'M' not in size:
            size = "{}mm".format(size)

        FileName = "Mounting_Wuerth_Inside-{size}_H{h}mm_{mpn}".format(size=size, h=part_params['h'], mpn=mpn)

        lib_name = "Mounting_Wuerth"

        ModelName = FileName.replace('.', '').replace('-', '_').replace('(', '').replace(')', '')

        FreeCAD.Console.PrintMessage('\r\n'+FileName+'\r\n')
        #FileName = modul.all_params[variant].file_name
        Newdoc = FreeCAD.newDocument(ModelName)
        print(Newdoc.Label)
        App.setActiveDocument(ModelName)
        App.ActiveDocument=App.getDocument(ModelName)
        Gui.ActiveDocument=Gui.getDocument(ModelName)

        color_keys = ["metal grey pins"]
        colors = [shaderColors.named_colors[key].getDiffuseInt() for key in color_keys]

        id = mech_params['id']
        if type(id) not in [float, int]:
            id = float(id[1:])
        cq_obj_data = generate(
                            id=id,
                            od=mech_params['od'],
                            od1=mech_params['od1'],
                            h1=mech_params['h1'],
                            h=part_params['h']
                            )

        color_i = colors[0] + (0,)
        show(cq_obj_data, color_i)

        doc = FreeCAD.ActiveDocument
        doc.Label = ModelName
        objs=GetListOfObjects(FreeCAD, doc)

        objs[0].Label = ModelName

        restore_Main_Tools()

        out_dir='{:s}{:s}.3dshapes'.format(global_3dpath, lib_name)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        used_color_keys = color_keys
        export_file_name=out_dir+os.sep+FileName+'.wrl'

        export_objects = []
        print('objs')
        print(objs)
        for i in range(len(objs)):
            export_objects.append(expVRML.exportObject(freecad_object = objs[i],
                    shape_color=color_keys[i],
                    face_colors=None))

        scale=1/2.54
        colored_meshes = expVRML.getColoredMesh(Gui, export_objects , scale)
        expVRML.writeVRMLFile(colored_meshes, export_file_name, used_color_keys, LIST_license)

        exportSTEP(doc,FileName,out_dir,objs[0])

        step_path = '{dir:s}/{name:s}.step'.format(dir=out_dir, name=FileName)

        L.addLicenseToStep(out_dir, '{:s}.step'.\
            format(FileName), LIST_license,
                LICENCE_Info.STR_licAuthor,
                LICENCE_Info.STR_licEmail,
                LICENCE_Info.STR_licOrgSys,
                LICENCE_Info.STR_licPreProc)

        FreeCAD.activeDocument().recompute()

        saveFCdoc(App, Gui, doc, FileName, out_dir)

        #FreeCADGui.activateWorkbench("PartWorkbench")
        if save_memory == False and check_Model==False:
            FreeCADGui.SendMsgToActiveView("ViewFit")
            FreeCADGui.activeDocument().activeView().viewAxometric()

        if save_memory == True or check_Model==True:
            doc=FreeCAD.ActiveDocument
            FreeCAD.closeDocument(doc.Name)

        if check_Model==True:
            runGeometryCheck(App, Gui, step_path,
                log, ModelName, save_memory=save_memory)

    with open('./wuerth_smt_inside_through.yaml', 'r') as params_stream:
        try:
            params = yaml.safe_load(params_stream)
        except yaml.YAMLError as exc:
            print(exc)

    with open(check_log_file, 'w') as log:
        for series in params:
            for mpn in params[series]['parts']:
                try:
                    export_one_part(params[series], mpn, log)
                except Exception as exeption:
                    traceback.print_exc()
                    break
