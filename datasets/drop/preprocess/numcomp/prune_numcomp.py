import os
import json
import argparse

from datasets.drop import constants

NUMBER_COMPARISON = ["were there more", "were there fewer", "which age group", "which group"]


def number_comparison_filter(question: str):
    question_lower = question.lower()
    football_ques_spans = ["first half", "second half", "quarter", "touchdown", "field goals"]
    relevant = True
    if any(span in question_lower for span in NUMBER_COMPARISON):
        or_split = question_lower.split(" or ")
        if len(or_split) != 2:
            relevant = False

        comma_split = question_lower.split(",")
        if len(comma_split) > 2:
            relevant = False

        # were there more / fewer -- remove these difficult football questions
        if any(span in question_lower for span in football_ques_spans):
            relevant = False
    else:
        relevant = False

    return relevant


def pruneDataset(input_json: str, output_json: str, output_txt: str) -> None:
    """ Prune dataset to only contain questions that qualify after certain NUM comparison question tests.
        Currently only keeping questions with a single passage SpanType answer.
    """

    # Input file contains single json obj with list of questions as jsonobjs inside it
    with open(input_json, "r") as f:
        dataset = json.load(f)

    num_input_qas = 0

    # List of tuples with (passage_id, passage_info)
    passage_id_infos = list(dataset.items())
    for (_, pinfo) in passage_id_infos:
        num_input_qas += len(pinfo[constants.qa_pairs])

    output_passage_dict = {}
    num_output_qas = 0

    txtfile = open(output_txt, "w")

    for passage_id, passage_info in dataset.items():
        qa_pairs = passage_info[constants.qa_pairs]
        relevant_qa_pairs = []

        for qa_pair in qa_pairs:
            keep = True
            question = qa_pair[constants.tokenized_question]

            # Number Comparison questions we care about
            if not number_comparison_filter(question):
                keep = False
                continue

            # Only SPAN type questions
            if constants.answer_type in qa_pair:
                if qa_pair[constants.answer_type] != constants.SPAN_TYPE:
                    keep = False
                    continue
            else:
                keep = False
                continue

            # To avoid duplication
            if keep:
                relevant_qa_pairs.append(qa_pair)
                question = qa_pair[constants.tokenized_question]
                passage = passage_info[constants.tokenized_passage]
                ans = qa_pair[constants.answer]
                txtfile.write(f"{question}\n")
                # txtfile.write(f"{passage}\n{ans}\n\n")

        if len(relevant_qa_pairs) == 0:
            continue

        passage_info[constants.qa_pairs] = relevant_qa_pairs
        num_output_qas += len(relevant_qa_pairs)

        # new_p_info = processPassage(passage_info)
        # if new_p_info is None:
        #     continue
        output_passage_dict[passage_id] = passage_info

    with open(output_json, "w") as outf:
        json.dump(output_passage_dict, outf, indent=4)

    txtfile.close()
    print(f"Number of input passages: {len(passage_id_infos)}\nNumber of input QA pairs: {num_input_qas}")
    print(f"Number of output passages: {len(output_passage_dict)}\nNumber of output QA pairs: {num_output_qas}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir")
    parser.add_argument("--output_dir")
    args = parser.parse_args()

    train_json = "drop_dataset_train.json"
    dev_json = "drop_dataset_dev.json"
    train_txt = "train.txt"
    dev_txt = "dev.txt"

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    input_trnfp = os.path.join(input_dir, train_json)
    input_devfp = os.path.join(input_dir, dev_json)

    output_trnfp = os.path.join(output_dir, train_json)
    output_devfp = os.path.join(output_dir, dev_json)
    output_trn_txt = os.path.join(output_dir, train_txt)
    output_dev_txt = os.path.join(output_dir, dev_txt)

    # args.input_json --- is the raw json from the DROP dataset
    pruneDataset(input_json=input_trnfp, output_json=output_trnfp, output_txt=output_trn_txt)

    # args.input_json --- is the raw json from the DROP dataset
    pruneDataset(input_json=input_devfp, output_json=output_devfp, output_txt=output_dev_txt)
