import os
import pymongo

rootdir = r'C:\Users\valen\Desktop\Abstracts' #path to folder with abstracts

# Columns we want to extract from raw txt data, just for reference
# ['Title', 'Type', 'NSF Org', 'Date', 'File', 'Award Number', 'Award Instr.',
#                                   'Prgm Manager', 'Start Date', 'Expires', 'Total Amt.', 'Investigator', 'Sponsor',
#                                   'NSF Program', 'Fld Applictn', 'Program Ref', 'Abstract']
if __name__ == '__main__':
    #Collection in database there we will store data
    db_documents = pymongo.MongoClient().ir.abstracts

    #Recuresevely walk over all files in folder to parse them and send to MongoDB
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if filename[0] == 'a' and filename[:-4:-1] == "txt": #Parse only txt files which matches document pattern
                with open(os.path.join(folder, filename), 'r') as file:

                    data = file.read().splitlines()
                    line_reduced_data = list()

                    for line in data:
                        if line.find(":") == 12:   #Due to structure of data, we always have ":" separator at position 12
                            line_reduced_data.append(line)
                        else:
                            line_reduced_data[-1]+=line

                    data_dict = {}
                    for line in line_reduced_data:
                        key, value = line.split(":",1) #Split only on first ":" to get key,value pair
                        data_dict[key.rstrip().replace(".","")]=' '.join(value.split()) # Delete needless spaces and
                        # remove dots due to MongoDB key limitations


                    db_documents.insert_one(data_dict) #Push entry to MongoDB



