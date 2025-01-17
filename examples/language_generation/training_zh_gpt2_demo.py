# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
from loguru import logger
import argparse
from transformers import BertTokenizerFast
import sys

sys.path.append('../..')
from textgen.language_generation import LanguageGenerationModel
from textgen.language_modeling import LanguageModelingModel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_file', default='../data/zh_article.txt', type=str, help='Training data file')
    parser.add_argument('--test_file', default='../data/zh_article.txt', type=str, help='Test data file')
    parser.add_argument('--model_type', default='gpt2', type=str, help='Transformers model type')
    parser.add_argument('--model_name', default='uer/gpt2-distil-chinese-cluecorpussmall', type=str,
                        help='Transformers model or path')
    parser.add_argument('--do_train', action='store_true', help='Whether to run training.')
    parser.add_argument('--do_predict', action='store_true', help='Whether to run predict.')
    parser.add_argument('--output_dir', default='./outputs/article_gpt2_zh_finetuned/', type=str,
                        help='Model output directory')
    parser.add_argument('--max_seq_length', default=50, type=int, help='Max sequence length')
    parser.add_argument('--num_epochs', default=10, type=int, help='Number of training epochs')
    parser.add_argument('--batch_size', default=32, type=int, help='Batch size')
    args = parser.parse_args()
    logger.info(args)

    if args.do_train:
        logger.info('Training...')
        train_args = {
            "reprocess_input_data": True,
            "overwrite_output_dir": True,
            "block_size": 512,
            "max_seq_length": args.max_seq_length,
            "learning_rate": 5e-6,
            "train_batch_size": args.batch_size,
            "gradient_accumulation_steps": 8,
            "num_train_epochs": args.num_epochs,
            "mlm": False,
            "output_dir": args.output_dir,
        }
        tokenizer = BertTokenizerFast.from_pretrained(args.model_name)
        model = LanguageModelingModel(args.model_type, args.model_name, args=train_args, tokenizer=tokenizer)
        model.train_model(args.train_file, eval_file=args.test_file)
        print(model.eval_model(args.test_file))

    if args.do_predict:
        logger.info('Predict...')
        # Use fine-tuned model
        tokenizer = BertTokenizerFast.from_pretrained(args.output_dir)
        model = LanguageGenerationModel(args.model_type, args.output_dir, args={"max_length": args.max_seq_length},
                                        tokenizer=tokenizer)

        prompts = [
            "你好啊",
            "好漂亮啊小姐姐",
            "你是军人吗？"
        ]
        for prompt in prompts:
            # Generate text using the model. Verbose set to False to prevent logging generated sequences.
            generated = model.generate(prompt, verbose=False)
            generated = generated[0]
            print("inputs:", prompt)
            print("outputs:", generated)


if __name__ == '__main__':
    main()
