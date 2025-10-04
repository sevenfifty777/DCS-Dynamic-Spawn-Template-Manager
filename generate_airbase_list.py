import csv
import os

# Map names for headers
map_names = {
    'AirbasesList_Afghanistan.csv': 'Afghanistan',
    'AirbasesList_Caucasus.csv': 'Caucasus',
    'AirbasesList_Falklands.csv': 'Falklands',
    'AirbasesList_GermanyCW.csv': 'Germany Cold War',
    'AirbasesList_Iraq.csv': 'Iraq',
    'AirbasesList_Kola.csv': 'Kola',
    'AirbasesList_MarianaIslands.csv': 'Mariana Islands',
    'AirbasesList_MarianaIslandsWWII.csv': 'Mariana Islands WWII',
    'AirbasesList_Nevada.csv': 'Nevada',
    'AirbasesList_Normandy.csv': 'Normandy',
    'AirbasesList_PersianGulf.csv': 'Persian Gulf',
    'AirbasesList_SinaiMap.csv': 'Sinai',
    'AirbasesList_Syria.csv': 'Syria',
    'AirbasesList_TheChannel.csv': 'The Channel'
}

csv_dir = 'Airbases List Files'
output_file = os.path.join(csv_dir, 'airbaseList.md')

with open(output_file, 'w', encoding='utf-8') as md:
    md.write('# DCS Airbase List by Map\n\n')
    md.write('This document lists all airbases available in each DCS map.\n\n')
    md.write('---\n\n')
    
    for csv_file in sorted(map_names.keys()):
        map_name = map_names[csv_file]
        csv_path = os.path.join(csv_dir, csv_file)
        
        if not os.path.exists(csv_path):
            continue
            
        md.write(f'## {map_name}\n\n')
        
        airdromes = []
        helipads = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                airbase_id = row['ID']
                name = row['Name']
                category = row['Category']
                
                if category == 'Airdrome':
                    airdromes.append((airbase_id, name))
                elif category == 'Helipad':
                    helipads.append((airbase_id, name))
        
        # Write Airdromes
        if airdromes:
            md.write(f'**Airdromes ({len(airdromes)}):**\n\n')
            for airbase_id, name in sorted(airdromes, key=lambda x: x[1]):
                md.write(f'- **{name}** (ID: {airbase_id})\n')
            md.write('\n')
        
        # Write Helipads
        if helipads:
            md.write(f'**Helipads ({len(helipads)}):**\n\n')
            for airbase_id, name in sorted(helipads, key=lambda x: x[1]):
                md.write(f'- **{name}** (ID: {airbase_id})\n')
            md.write('\n')
        
        md.write(f'**Total: {len(airdromes) + len(helipads)} locations**\n\n')
        md.write('---\n\n')

print(f'Generated {output_file}')
