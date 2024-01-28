# DivLog

DivLog is an online LLM-based log parsing framework via in-context learning. It supports various LLMs as engines through API for high-quality parsing results.

### Running

Install the required enviornment:
```
pip install -r requirements.txt
```

Run the following scripts to start the demo by replacing "sk-xxx" to your own OpenAI API Key:

```
python demo.py -key sk-xxx
```

Run the following scripts to execute the benchmark by replacing "sk-xxx" to your own OpenAI API Key:

```
python benchmark.py -key sk-xxx
```

Re-generate embeddings by replacing "sk-xxx" to your own OpenAI API Key:

```
python embedding.py -key sk-xxx
```

If you wish to re-run all the results (which may cost much time and api budget), please delete the `results` repository:

```
rm -r results
```

#### Attention:

OpenAI has [shut down](https://platform.openai.com/docs/deprecations/2023-07-06-gpt-and-embeddings) the *Text Completion API* for the GPT-3 model series (`ada`,`babbage`,`curie`,`davinci`) as of January 4th, 2024. If you wish to apply the DivLog framework on other OpenAI *Chat Completion APIs* and re-run all the results, you may need to modify the API request in `BatchParse` of `DivLog.py`. Specifically, you need to replace the original API request design for GPT-3 models with the latest Chat Completion API:

```python
### Replace it
response = openai.Completion.create(
                                    model=model, 
                                    prompt=instruction + "\n\n\n" + prompt + "<prompt>:" + line.strip() + "\n<extraction>: ", 
                                    temperature=temperature,
                                    max_tokens=token_len)
```

More details about APIs can be found [here](https://platform.openai.com/docs/api-reference/chat).


### Benchmark

Running the benchmark script on Loghub_2k datasets, you could obtain the following results.

|      Dataset | Parsing Accuracy | Precision Template Accuracy | Recall Template Accuracy | Grouping Accuracy |
|:------------:|:-----------------|:----------------------------|:-------------------------|:------------------|
|     HealthApp| 0.9955           | 0.947368                    | 0.960000                 | 0.8700            |
|       OpenSSH| 0.9450           | 0.961538                    | 0.925926                 | 0.7530            |
|   Thunderbird| 0.9850           | 0.934211                    | 0.953020                 | 0.9630            |
|     Proxifier| 1.0000           | 1.000000                    | 1.000000                 | 1.0000            |
|        Apache| 1.0000           | 1.000000                    | 1.000000                 | 1.0000            |
|           HPC| 0.9970           | 0.914894                    | 0.934783                 | 0.9270            |
|     Zookeeper| 0.9980           | 0.886792                    | 0.940000                 | 0.7360            |
|     OpenStack| 0.9995           | 0.953488                    | 0.953488                 | 0.9785            |
|          HDFS| 0.9990           | 0.866667                    | 0.928571                 | 0.8880            |
|         Spark| 0.9995           | 0.972222                    | 0.972222                 | 1.0000            |
|          BGL | 0.9870           | 0.917355                    | 0.925000                 | 0.9720            |
|      Windows | 0.9980           | 0.918367                    | 0.900000                 | 0.9980            |
|        Linux | 0.9970           | 0.957627                    | 0.957627                 | 0.9940            |
|      Android | 0.9425           | 0.830409                    | 0.855422                 | 0.9300            |
|          Mac | 0.8625           | 0.675595                    | 0.665689                 | 0.8455            |
|       Hadoop | 0.9960           | 0.982609                    | 0.991228                 | 0.9940            |


### 🔥 Citation

If you use the code or benchmarking results in your publication, please kindly cite the following papers.

+ [**ICSE'24**] Junjielong Xu, Ruichun Yang, Yintong Huo, Chengyu Zhang, and Pinjia He. [DivLog: Log Parsing with Prompt Enhanced In-Context Learning](https://doi.org/10.1145/3597503.3639155). *IEEE/ACM 46th International Conference on Software Engineering (ICSE)*, 2024.
+ [**ICSE'19**] Jieming Zhu, Shilin He, Jinyang Liu, Pinjia He, Qi Xie, Zibin Zheng, Michael R. Lyu. [Tools and Benchmarks for Automated Log Parsing](https://arxiv.org/pdf/1811.03509.pdf). *International Conference on Software Engineering (ICSE)*, 2019.
