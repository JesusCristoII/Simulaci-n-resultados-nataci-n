import pandas as pd
import re
from PyPDF2 import PdfReader


class Simulation:


    def __init__(self, path= None):
        
        if path is None:
            self.path = 'series.pdf'
        else:
            self.path = path

    
    def __process_pdf(self):

        reader = PdfReader(self.path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text


    def __get_data(self):

        data = []

        text = self.__process_pdf()

        for line in text:
            
            # Look for the gender
            if re.search(r'Fem.*', line):
                gender = 'Femenino'
            elif re.search(r'Masc.*', line):
                gender = 'Masculino'
            
            # Look for the prueba
            if (p := re.search(r'Prueba\s.+\.,\s*(\d{2,4}m\s)\s*(Libre|Espalda|Braza|Mariposa|Estilos).*', line)):
                prueba = p.group(1) + p.group(2)
            
            # Relay
            elif (p := re.search(r'Prueba\s.+\.,\s*(4 x 50m)\s*(Libre|Estilos).*', line)):
                prueba = p.group(1) + p.group(2)
            
            # Look for the name of the swimmer
            elif (s := re.search(r'[0-9](.+,\s.+)\s\d{2}\s(.+)\s(.+)\s_.+$', line)):
                swimmer = s.group(1)
                club = s.group(2)
                time = s.group(3)
                data.append((swimmer, gender, club, prueba, time))

            # Look for the name of the relay
            elif (s := re.search(r'[0-9](.+\s.+)\s\d{2}\s(.+)\s(.+)\s_.+$', line)):
                swimmer = s.group(1)
                club = s.group(2)
                time = s.group(3)
                data.append((swimmer, gender, club, prueba, time))

        df = pd.DataFrame(data, columns= ['Name', 'Gender','Club', 'Prueba', 'Time'])
        df['Time'].replace('NT', '59:59.59', inplace= True)
        df['Time'] = df['Time'].apply(lambda x: int(x[0:x.index(':')]) * 60 + int(x[x.index(':')+1:x.index('.')]) + float('0.'+x[-2:]) if len(x) > 5 else float(x))
        return df
    

    def get_punctuations(self, gender):

        df = self.__get_data()

        punctuations = [22,17,14,13,12,11,10,9,8,7,6,5,4,3,2,1]

        df = df[df['Gender'] == gender]

        points = {club : 0 for club in df['Club'].unique()}

        for prueba in df['Prueba'].unique():

            swimmers = df[(df['Prueba'] == prueba) & (df['Gender'] == gender)]

            swimmers.sort_values(by= 'Time', ascending= True, inplace= True)

            for i in range(swimmers.shape[0]):

                linea = swimmers.iloc[i]
                # Relay
                if 'x' in prueba:
                    points[linea['Club']] += 2 * punctuations[i]
                else:
                    points[linea['Club']] += punctuations[i]

        results = sorted(points.items(), key= lambda x: -x[1])
        return results
    

if __name__ == '__main__':

    simulator = Simulation()
    print(simulator.get_punctuations(gender= 'Masculino'))