# main.py

from core.flow.flows import data_treatment_flow
from core.utils import configure_text_output, log


def main():
    configure_text_output()
    log("DATA TREATMENT")
    log("Modo de execucao: Prefect flow de tratamento por planilha ingest")
    data_treatment_flow()


if __name__ == "__main__":
    main()
