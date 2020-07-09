import xml.etree.ElementTree as ET
from pprint import pprint
import shutil
import json
import os
import glob
import sys

def pathChanger(FileName,current_path):
    print("*************")
    print(current_path)
    print("*************")
    from os.path import expanduser
    home_path = expanduser("~")
    splited_path = current_path.split('/')
    current_FileName = splited_path[len(splited_path) - 3]
    template_home_path = '/' + str(splited_path[1]) + '/' + str(splited_path[2])
    derived_path_filename = current_path.replace(current_FileName, FileName)
    derived_path = derived_path_filename.replace(template_home_path,home_path)
    return derived_path

config_data = {}

def main(argv):
    print("################################# File Path ##########################################")
    currentPath = os.getcwd()
    print('Current Path ----- > ', currentPath)
    foldername = os.path.basename(currentPath)
    print("Directory name ----- > " + foldername)
#----------------------------------- Print input parameters -------------------------------------
    print("############################# Input Parameters #######################################")
    print('Name Gain Peaking_time L0offset Threshold')
    print("######################### Input Parameters as List ###################################")
    print('File Name ----- > ',argv[0])
    print('Gain ----- > ',argv[1])
    print('Peaking_time ----- > ',argv[2])
    print('L0offset ----- > ',argv[3])
    print('Threshold ----- > ',argv[4])
    print("################################## ERROR #############################################")
#----------------------------------- import config data file ------------------------------------
    check_Gain = False
    check_Peaking_time = False
    check_config_file = False
    try:
        with open('Template/data.json','r') as f:
            global config_data
            config_data = json.load(f)
    except IOError:
        print("Config File does not exist !")
        check_config_file = True
    if check_config_file == False:
        try:
            config_data['gain'][argv[1]]
            check_Gain = True
        except KeyError:
            print("Gain value is not correct !")
            pass
        try:
            config_data['peaking_time'][argv[2]]
            check_Peaking_time = True
        except KeyError:
            print("Peaking_time value is not correct !")
            pass
        if check_Gain and check_Peaking_time == True:
            print("Everything is OK")
    print("######################################################################################")
    if check_Gain and check_Peaking_time and check_config_file == False:
        #print("############################### Data from config file ################################")
    #------------------------------------- A prime calculation --------------------------------------
        AA = []
        for i in range(len(config_data['A'])):
            AA.append(round(1 / config_data['A'][i],2))
    #------------------------------------- B prime calculation --------------------------------------
        BB = []
        for i in range(len(config_data['B'])):
            BB.append(round(-config_data['B'][i] / config_data['A'][i],2))
    #------------------------------------- sdt_dac calculation --------------------------------------
        sdt_dac_arr = []
        for i in range(len(AA)):
            sdt_dac_arr.append(int(round(AA[i] * (config_data['baseline'][i] + int(argv[4])) +  BB[i])))
        #print('sdt_dac ----- > ',sdt_dac_arr)
    #---------------------------------- Print ip, chip, baseline ------------------------------------
        #print('ip ----- > ',config_data['ip'])
        #print('chip ----- > ',config_data['chip'])
        #print('baseline ----- > ',config_data['baseline'])
        #print("################################## JSON full files ###################################")
    #--------------------------------------- JSON Files list ----------------------------------------
        txtfiles = []
        for file in glob.glob("Template/data/*.json"):
            txtfiles.append(file)

        #print('JSONfiles ----- > ',txtfiles)
    #--------------------------------- filtration JSON Files list -----------------------------------
        #print("################################# Target JSON files ##################################")
        filtredJsonFile = []
        for jsonFile in txtfiles:
            if "globals_board" in jsonFile:
                filtredJsonFile.append(jsonFile)
        #print('Filtred JSONfiles ----- > ',filtredJsonFile)
    #--------------------------- sdt_dac value correction in JSON files -----------------------------
        sdt_dacFromfiles = []
        for f in filtredJsonFile:
            with open(f, 'r') as outfile:
                load = json.load(outfile)
                try:
                    sdt_dacFromfiles.append(load['vmm_global_config']['configuration']['sdt_dac'])
                except KeyError:
                    pass
        #print("################################## sdt_dac Results ###################################")
        #print('sdt_dac_values_from_json_files ----- > ',sdt_dacFromfiles)
    #--------------------------- gather all files board and chip number -----------------------------
        fileName_ip_chip = {}
        for f in filtredJsonFile:
            with open(f, 'r') as outfile:
                Tempload = json.load(outfile)
                fileName_ip_chip.update({f:[Tempload['vmm_global_config']['board_id'],Tempload['vmm_global_config']['vmm_id']]})
    #----------------------------- all board and chip number indexes --------------------------------
        index_ip_chip = {}
        for i in range(len(config_data['ip'])):
            index_ip_chip.update({ i:[config_data['ip'][i],config_data['chip'][i]] })
    #--------------------- Determine file name and proper sdt_dac for corecting ---------------------
        print("###################### Target JSON files with proper parameters  #####################")
        FileName_sdt_dac = {}
        for key in fileName_ip_chip:
            for k in index_ip_chip:
                if fileName_ip_chip[key] == index_ip_chip[k]:
                    FileName_sdt_dac.update({ key : [ index_ip_chip[k], config_data['gain'][argv[1]], config_data['peaking_time'][argv[2]], argv[3], sdt_dac_arr[k] ] })
                    break
        pprint(FileName_sdt_dac)
    #-------------------------- Correct all sdt_dac parameter in Json files -------------------------
        for key in FileName_sdt_dac:
            fileName_ip_chip = {}
            with open(key, 'r') as inputFile:
                recentJsonFile = json.load(inputFile)
            recentJsonFile['vmm_global_config']['configuration']['sdt_dac'] = FileName_sdt_dac[key][4]
            recentJsonFile['vmm_global_config']['configuration']['sg'] = int(config_data['gain'][argv[1]])
            recentJsonFile['vmm_global_config']['configuration']['st'] = int(config_data['peaking_time'][argv[2]])
            recentJsonFile['vmm_global_config']['configuration']['l0offset'] = int(argv[3])
            with open(key, 'w') as outputFile:
                json.dump(recentJsonFile,outputFile,indent = 4)
#################################################################################################
        #print("########################## Target JSON files Paths changing  #########################")
        tree = ET.parse('Template/fine_description.xml')
        root = tree.getroot()

        FileName = 'fine_config_' + str(argv[0])

        path_global_json = []
        path_channel_json = []
        path_common_json = []

        for component in root.findall("./board/configuration"):
            for global_component in component.findall("./global"):
                path_global_json.append(global_component.text)

            for channel_componen in component.findall("./channel"):
                path_channel_json.append(channel_componen.text)

            for common_componen in component.findall("./common"):
                path_common_json.append(common_componen.text)

        current_full_json_paths = path_global_json + path_channel_json + path_common_json

        derived_path_global_json = []
        derived_path_channel_json = []
        derived_path_common_json = []
        
        for path in path_global_json:
            derived_path_global_json.append(pathChanger(FileName,path))

        for path in path_channel_json:
            derived_path_channel_json.append(pathChanger(FileName,path))

        for path in path_common_json:
            derived_path_common_json.append(pathChanger(FileName,path))

        full_json_paths = derived_path_global_json + derived_path_channel_json + derived_path_common_json

        #pprint(current_full_json_paths)
        #pprint(full_json_paths)

        for i in range(len(full_json_paths)):
            for elem in root.getiterator():
                elem.text = elem.text.replace(current_full_json_paths[i], full_json_paths[i])
        tree.write("Template/fine_description.xml",encoding="UTF-8",xml_declaration=True)

        derived_FileName = currentPath + '/' + 'fine_config_' + argv[0]

        if os.path.exists(derived_FileName):
            shutil.rmtree(derived_FileName)

        os.makedirs(derived_FileName)

        shutil.copy(currentPath + '/Template/fine_description.xml', derived_FileName)
        shutil.copytree(currentPath + '/Template/data', derived_FileName + '/data')
            
        print("####################################### Done #########################################")
#################################################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
    #main(['hi','9','200','4095','50'])
    # python ./config.py test 9 200 4095 50