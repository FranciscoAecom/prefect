import unittest

import pandas as pd

from core.transforms.attribute_transforms import clean_whitespace


class AttributeTransformsTests(unittest.TestCase):
    def test_clean_whitespace_trims_and_collapses_text_values(self):
        dataframe = pd.DataFrame(
            {
                "texto": ["  valor   com   espaco  ", None, "linha\nquebrada"],
                "numero": [1, 2, 3],
            }
        )

        result = clean_whitespace(dataframe)

        self.assertEqual(result.loc[0, "texto"], "valor com espaco")
        self.assertTrue(pd.isna(result.loc[1, "texto"]))
        self.assertEqual(result.loc[2, "texto"], "linha quebrada")
        self.assertEqual(result["numero"].tolist(), [1, 2, 3])

    def test_clean_whitespace_handles_categorical_text_values(self):
        dataframe = pd.DataFrame(
            {
                "status": pd.Series(
                    ["  Excluído  ", "Ativo"],
                    dtype="category",
                )
            }
        )

        result = clean_whitespace(dataframe)

        self.assertEqual(result["status"].tolist(), ["Excluído", "Ativo"])


if __name__ == "__main__":
    unittest.main()
