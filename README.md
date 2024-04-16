## Setup and Installation

1. Execute following commands:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. Download lates version Neo4j Desktop from: https://neo4j.com/deployment-center/

3. Run the batch file: DownloadApocAndRunNeo4j.bat as administrator, be sure to check the contents of the file as the paths will need to be set accordingly

   1. `cd /d "C:\Program Files\neo4j-community-5.18.0\plugins"` change to the correct path of the plugins folder in your Neo4j installation

   2. `cd /d "C:\Program Files\neo4j-community-5.18.0\bin"` change to the correct path of the bin folder in your Neo4j installation

## Usage

For ease of use, use the main.py file in the root directory to run the program, this way you can easily access the modules and classes in the program.

## Contributors

- [Oscar Theelen](https://github.com/Ozziehman)
- [Menno Rompelberg](https://github.com/MasterDisaster7)
- [Axel Frederiks](https://github.com/ProgrammerGhostPrK)
- [Jonah Siemers](https://github.com/Doomayy)
