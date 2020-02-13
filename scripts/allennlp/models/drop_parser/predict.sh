#!/usr/bin/env

# PACKAGE TO BE INCLUDED WHICH HOUSES ALL THE CODE
INCLUDE_PACKAGE=semqa
export GPU=0
export BEAMSIZE=1
export DEBUG=true

# SAVED MODEL
MODEL_DIR=./resources/semqa/checkpoints/drop/date_num/date_ydre_num_hmyw_cnt_rel_600/drop_parser/TOKENS_qanet/ED_100/RG_1e-07/MODELTYPE_encoded/CNTFIX_false/aux_true/SUPEPOCHS_5/S_1000/Model/
MODEL_TAR=${MODEL_DIR}/model.tar.gz
PREDICTION_DIR=${MODEL_DIR}/predictions
mkdir ${PREDICTION_DIR}

DATASET_DIR=./resources/data/drop/date_num

# This should contain:
# 1. drop_dataset_mydev.json and drop_dataset_mytest.json
# 2. A folder containing multiple sub-dataset folders, each with mydev and mytest .json
DATASET_NAME=date_ydNEW_num_hmyw_cnt_rel_600_10p


FULL_VALFILE=${DATASET_DIR}/${DATASET_NAME}/drop_dataset_mydev.json
PREDICTION_FILE=${PREDICTION_DIR}/${DATASET_NAME}_dev_numstepanalysis.tsv
PREDICTOR=drop_analysis_predictor
# PREDICTOR=drop_parser_predictor

allennlp predict --output-file ${PREDICTION_FILE} \
                     --predictor ${PREDICTOR} \
                     --cuda-device ${GPU} \
                     --include-package ${INCLUDE_PACKAGE} \
                     --silent \
                     --batch-size 1 \
                     --use-dataset-reader \
                     --overrides "{"model": { "beam_size": ${BEAMSIZE}, "debug": ${DEBUG}}}" \
                    ${MODEL_TAR} ${FULL_VALFILE}


#for EVAL_DATASET in datecomp_full year_diff count_filterqattn hmyw_filter relocate_wprog numcomp_full
## for EVAL_DATASET in relocate_wprog
#do
#    DATASET_DIR=./resources/data/drop/${SUBFOLDER}/${EVAL_DATASET}
#    TRAINFILE=${DATASET_DIR}/drop_dataset_train.json
#    VALFILE=${DATASET_DIR}/drop_dataset_dev.json
#
#    TESTFILE=${VALFILE}
#
#    ANALYSIS_FILE=${PREDICTION_DIR}/${EVAL_DATASET}_dev_analysis.tsv
#    PREDICTION_FILE=${PREDICTION_DIR}/${EVAL_DATASET}_dev_pred.txt
#    EVALUATION_FILE=${PREDICTION_DIR}/${EVAL_DATASET}_dev_eval.txt
#    # PREDICTOR=drop_analysis_predictor
#    PREDICTOR=drop_parser_predictor
#
#    ###################################################################################################################
#
#    # allennlp predict --output-file ${ANALYSIS_FILE} \
#    allennlp predict --output-file ${PREDICTION_FILE} \
#                     --predictor ${PREDICTOR} \
#                     --cuda-device ${GPU} \
#                     --include-package ${INCLUDE_PACKAGE} \
#                     --silent \
#                     --batch-size 1 \
#                     --use-dataset-reader \
#                     --overrides "{"model": { "beam_size": ${BEAMSIZE}, "debug": ${DEBUG}}}" \
#                    ${MODEL_TAR} ${TESTFILE}
#
#    allennlp evaluate --output-file ${EVALUATION_FILE} \
#                      --cuda-device ${GPU} \
#                      --include-package ${INCLUDE_PACKAGE} \
#                      ${MODEL_TAR} ${TESTFILE}
#
#    echo -e "Predictions file saved at: ${PREDICTION_FILE}"
#    echo -e "Evaluations file saved at: ${EVALUATION_FILE}"
#done
