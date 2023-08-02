from apis.sensitive_api import BaiduApi, WordsCheckApi, HuaweiApi, YidunApi


def run_apis(data_path):
    # sensitive_api = WordsCheckApi(data_path)
    # sensitive_api = BaiduApi(data_path)
    # sensitive_api = HuaweiApi(data_path)
    sensitive_api = YidunApi(data_path, "a5b11e1b9b22de6640a88f002ef2ff5a",
                             "ed0e86ec971cb8d0e1be2152b7b06b5b", "d3894efafef52620ac77f94c8f13ebdc")
    sensitive_api.run_apis()


def parse_results():
    with open("./results/wordscheck_results.csv", 'w') as f:

        with open("./results/words_check_results.csv", 'r') as csvfile:
            next_line = []
            for idx, line in enumerate(csvfile.readlines()):
                if idx == 0:
                    f.write(line + "\n")
                else:
                    new_line = "".join(line.strip().split(","))
                    if new_line.strip() == "":
                        next_line.append("NA")
                    else:
                        next_line.append(new_line)
                    if len(next_line) == 3:
                        print(next_line)
                        f.write(",".join(next_line) + "\n")
                        next_line = []


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_apis('data/202307_POST_TEXT_POST_TEXT_task_id_35688.csv')
    # parse_results()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
