# main.py

from core.flow.flows import data_pipeline_flow
from core.utils import configure_text_output, log


def main():
    configure_text_output()
    log("DATA PIPELINE")
    log("Modo de execucao: Prefect flow por planilha ingest")
    data_pipeline_flow()


if __name__ == "__main__":
    main()
