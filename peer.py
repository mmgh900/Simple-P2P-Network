import requests
from essential_generators import DocumentGenerator

gen = DocumentGenerator()

for i in range(1, 30):
    with open(f'./ownedFiles/file{i}', 'w') as file:
        file.write(f'*** FILE NUMBER {i} ***\n')
        file.write(gen.sentence())