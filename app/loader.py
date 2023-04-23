import gensim
import torch
import underthesea
import numpy as np
from typing import List
from transformers import (
    AutoModel,
    AutoTokenizer,
    T5ForConditionalGeneration,
    T5Tokenizer,
)
from sklearn.preprocessing import MultiLabelBinarizer

from app.core.config import project_config


class Loader:
    def __init__(self) -> None:
        if torch.cuda.is_available():
            self.__device = torch.device("cuda")

            print("There are %d GPU(s) available." % torch.cuda.device_count())

            print("We will use the GPU:", torch.cuda.get_device_name(0))
        else:
            print("No GPU available, using the CPU instead.")
            self.__device = torch.device("cpu")

        # Load model vector hóa
        self.__phobert = AutoModel.from_pretrained("vinai/phobert-base").to(self.__device)
        self.__tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

        # # Load model summarization
        # self.model = T5ForConditionalGeneration.from_pretrained("NlpHUST/t5-small-vi-summarization").to(device)
        # self.t5tokenizer = T5Tokenizer.from_pretrained("NlpHUST/t5-small-vi-summarization")

        self.__stop_word_data = np.genfromtxt(
            project_config.STOPWORD_PATH, dtype="str", delimiter="\n", encoding="utf8"
        ).tolist()
        self.__multilabel_binarizer = MultiLabelBinarizer(sparse_output=True)

    def feature_engineering(self, data: List):
        features_set = []
        for line in data:
            line = gensim.utils.simple_preprocess(line)  # Tiền xử lý dữ liệu
            line = " ".join(line)
            line = underthesea.word_tokenize(line, format="text")  # Segment word
            line = " ".join(
                [word for word in line.split() if word not in self.__stop_word_data]
            )
            # if len(line.split()) > 100: # Summary long text
            # self.model.eval()
            #   tokenized_text = self.t5tokenizer.encode(line, return_tensors="pt").to(self.__device)
            #   summary_ids = model.generate(
            #                       tokenized_text,
            #                       max_length=256,
            #                       num_beams=5,
            #                       repetition_penalty=2.5,
            #                       length_penalty=1.0,
            #                       early_stopping=True
            #                   )
            #   line = self.t5tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            line = self.__tokenizer(line, truncation=True).input_ids  # tokenizer
            input_ids = torch.tensor([line]).to(torch.long)
            with torch.no_grad():  # Lấy features dầu ra từ BERT
                features = self.__phobert(input_ids)
            v_features = features[0][:, 0, :].numpy()
            features_set.append(v_features[0])
        features_set = np.array(features_set)
        return features_set
        
    def multilabel_binarizing(self, raw_data):
        data = [[i] for i in raw_data]
        return self.__multilabel_binarizer.fit_transform(data).toarray()

loader = Loader()