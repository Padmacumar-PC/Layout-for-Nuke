#*********************************************************************
# content = Layouts render passes in Nuke
#
# version = 1.1.0
# date = 2022-10-30
#
# how to = main_pass_list(),
#          component_pass_list(),
#          zdepth_pass(),
#          multimatte_pass()
#
# dependencies = Nuke
# todos = Create dropdown list for file paths,
#         Add Denoiser in the main pass selection,
#         Create Backdrops for read nodes
#
# license = MIT
# author = Padmacumar Prabhaharan <padmacumar@gmail.com>
#*********************************************************************


import os
import nuke
import nukescripts


#*********************************************************************
# CONSTANT VARIABLES

FOLDER_PATH = panel.value('file path')
PASS_LIST = os.listdir(FOLDER_PATH)

MAIN_PASS = ['rgba']

COMPONENT_PASS = ['GI', 
                  'shadow', 
                  'reflect', 
                  'refract', 
                  'diffuse', 
                  'specular', 
                  'lighting']

UTILITY_PASS = ['zDepth', 
                'multimatte']

#*********************************************************************
# UI
panel = nuke.Panel("Render files location")
panel.setWidth(800)
panel.addFilenameSearch('file path', '')

button_press = panel.show()
print(button_press)

#*********************************************************************
# MAIN PASS
def main_pass_list():
    for m_passes in MAIN_PASS:
        if m_passes in PASS_LIST:
            pass_folder = FOLDER_PATH + m_passes + "/"
            
            for seq in nuke.getFileNameList(pass_folder):
                read_node = nuke.nodes.Read(name = m_passes)
                read_node.knob('file').fromUserText(pass_folder + seq)

                for de_sel in nuke.selectedNodes():
                    de_sel.knob('selected').setValue(False)

                sel = nuke.toNode(m_passes)
                sel.knob('selected').setValue(True)
                selection = nuke.selectedNodes()

                nuke.message("RGBA file successfully created")

        else:
            break

#*********************************************************************
# COMPONENTS
def component_pass_list():
    for c_passes in COMPONENT_PASS:
        if c_passes in PASS_LIST:
            pass_folder = FOLDER_PATH + c_passes + "/"
            
            selection = nuke.selectedNodes()
            
            if selection:

                for sel in selection:
                    sel.knob('selected').setValue(True)    
                    sel_posx = sel['xpos'].getValue()
                    sel_posy = sel['ypos'].getValue()
            else:
                nuke.message("Select or Create the RGBA read file to start the execution")
                break
                
            for seq in nuke.getFileNameList(pass_folder):
                merge_node1 = nuke.createNode("Merge", "operation difference", False)
                merge_node1['xpos'].setValue(sel_posx)
                merge_node1['ypos'].setValue(sel_posy + 200)
                merge_n1_posx = merge_node1['xpos'].getValue()
                merge_n1_posy = merge_node1['ypos'].getValue()
                merge_node1.setInput(0, sel)

                read_node = nuke.nodes.Read(name = c_passes)
                read_node.knob('file').fromUserText(pass_folder + seq)
                read_node['xpos'].setValue(merge_n1_posx - 200)
                read_node['ypos'].setValue(merge_n1_posy - 32)
                read_node_posx = read_node['xpos'].getValue()
                read_node_posy = read_node['ypos'].getValue()

                dot_node_corner = nuke.createNode("Dot", "", False)
                dot_node_corner['xpos'].setValue(read_node_posx + 33)
                dot_node_corner['ypos'].setValue(read_node_posy + 155)

                merge_node2 = nuke.createNode("Merge", "operation plus", False)
                merge_node2['xpos'].setValue(merge_n1_posx)
                merge_node2['ypos'].setValue(merge_n1_posy + 120)

                merge_node1.setInput(1, read_node)
                dot_node_corner.setInput(0, read_node)
                merge_node2.setInput(1, dot_node_corner)
                merge_node2.setInput(0, merge_node1)

                selection = nuke.selectedNodes()

        else:
            nuke.message("Components successfully created")

#*********************************************************************
# DEPTH
def zdepth_pass():
    for u_passes in UTILITY_PASS:
        if u_passes in PASS_LIST:
            pass_folder = FOLDER_PATH + u_passes + "/"
            
            rgba_pass = nuke.toNode('rgba')

            if rgba_pass == None:
                nuke.message("Please create an RGBA file to prepare the ZDefocus Group")
                break

            rgba_pass_posx = rgba_pass['xpos'].getValue()
            rgba_pass_posy = rgba_pass['ypos'].getValue()

            if 'zDepth' in pass_folder:
                for seq in nuke.getFileNameList(pass_folder):
                    read_node = nuke.nodes.Read(name = u_passes)
                    read_node.knob('file').fromUserText(pass_folder + seq)
                    read_node['xpos'].setValue(rgba_pass_posx + 500)
                    read_node['ypos'].setValue(rgba_pass_posy)
                    read_node_posx = read_node['xpos'].getValue()
                    read_node_posy = read_node['ypos'].getValue()
                
                for de_sel in nuke.selectedNodes():
                    de_sel.knob('selected').setValue(False)

                shufflecopy_node = nuke.nodes.ShuffleCopy(name="Shuffle_zDepth")
                shufflecopy_node['red'].setValue('red1')
                shufflecopy_node['out'].setValue('depth')
                shufflecopy_node['xpos'].setValue(read_node_posx)
                shufflecopy_node['ypos'].setValue(read_node_posy + 150)
                shufflecopy_node_posx = shufflecopy_node['xpos'].getValue()
                shufflecopy_node_posy = shufflecopy_node['ypos'].getValue()

                zdepth_node = nuke.createNode("ZDefocus2")
                zdepth_node.setInput(0, shufflecopy_node)
                zdepth_node['xpos'].setValue(shufflecopy_node_posx)
                zdepth_node['ypos'].setValue(shufflecopy_node_posy + 100)

                for de_sel in nuke.selectedNodes():
                    de_sel.knob('selected').setValue(False)


                dot_node = nuke.createNode("Dot", "", False)
                input_label = 'connect to Layout merge'
                dot_node['xpos'].setValue(shufflecopy_node_posx - 150)
                dot_node['ypos'].setValue(shufflecopy_node_posy - 20)
                dot_node.knob('label').setValue(input_label)

                shufflecopy_node.setInput(1, read_node)
                shufflecopy_node.setInput(0, dot_node)
            
                for de_sel in nuke.selectedNodes():
                    de_sel.knob('selected').setValue(False)

                nuke.message("ZDefocus Group successfully created as Ultility")

#*********************************************************************
# MULTIMATTES
def multimatte_pass():
    for u_passes in UTILITY_PASS:
        if u_passes in PASS_LIST:
            pass_folder = FOLDER_PATH + u_passes + "/"
            
            rgba_pass = nuke.toNode('rgba')

            if rgba_pass == None:
                nuke.message("Please create an RGBA file to prepare the Matte Group")
                break

            rgba_pass_posx = rgba_pass['xpos'].getValue()
            rgba_pass_posy = rgba_pass['ypos'].getValue()

        
            if 'multimatte' in pass_folder:
                for seq in nuke.getFileNameList(pass_folder):
                    read_node = nuke.nodes.Read(name = u_passes)
                    read_node.knob('file').fromUserText(pass_folder + seq)
                    read_node['xpos'].setValue(rgba_pass_posx + 500)
                    read_node['ypos'].setValue(rgba_pass_posy + 500)
                    read_node_posx = read_node['xpos'].getValue()
                    read_node_posy = read_node['ypos'].getValue()

                    s1_node = nuke.nodes.Shuffle(name = 'Red_Shuffle')
                    s1_node['red'].setValue('red1')
                    s1_node['blue'].setValue('red1')
                    s1_node['green'].setValue('red1')
                    s1_node['alpha'].setValue('red1')
                    s1_node['xpos'].setValue(read_node_posx - 100)
                    s1_node['ypos'].setValue(read_node_posy + 150)
                    s1_node.setInput(0, read_node)

                    s2_node = nuke.nodes.Shuffle(name = 'Green_Shuffle')
                    s2_node['red'].setValue('green1')
                    s2_node['blue'].setValue('green1')
                    s2_node['green'].setValue('green1')
                    s2_node['alpha'].setValue('green1')
                    s2_node['xpos'].setValue(read_node_posx)
                    s2_node['ypos'].setValue(read_node_posy + 150)
                    s2_node.setInput(0, read_node)

                    s3_node = nuke.nodes.Shuffle(name = 'Blue_Shuffle')
                    s3_node['red'].setValue('blue1')
                    s3_node['blue'].setValue('blue1')
                    s3_node['green'].setValue('blue1')
                    s3_node['alpha'].setValue('blue1')
                    s3_node['xpos'].setValue(read_node_posx + 100)
                    s3_node['ypos'].setValue(read_node_posy + 150)
                    s3_node.setInput(0, read_node)

                    for de_sel in nuke.selectedNodes():
                        de_sel.knob('selected').setValue(False)

                    nuke.message("Matte Group successfully created as Ultility")
