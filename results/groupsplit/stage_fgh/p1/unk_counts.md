### P1: unknown pieces (id 0) in the real token sequences (call-token store, old tokenizer)

Id check: {"sentencepiece_unk_id": 0, "sentencepiece_unk_piece": "<unk>", "sentencepiece_bos_id": 1, "sentencepiece_eos_id": 2, "sentencepiece_pad_id": -1, "pieces": 50000, "unseen_character_encoding": [435, 49966, 0, 49966, 434], "vocab_json_entries": 50001, "vocab_json_pad": 0, "vocab_json_unk": 1}

| population | class | scope | reports | share with >= 1 unknown (%) | median count (all) | median count (affected) | mean count | max |
|---|---|---|---|---|---|---|---|---|
| January training (group split) | all | first 512 tokens | 66580 | 32.836 | 0 | 1 | 0.6900 | 20 |
| January training (group split) | all | whole report | 66580 | 66.679 | 4 | 4 | 2.6502 | 244 |
| January training (group split) | malware | first 512 tokens | 45073 | 41.932 | 0 | 1 | 0.7970 | 10 |
| January training (group split) | malware | whole report | 45073 | 69.882 | 4 | 4 | 2.7994 | 98 |
| January training (group split) | benign | first 512 tokens | 21507 | 13.772 | 0 | 4 | 0.4657 | 20 |
| January training (group split) | benign | whole report | 21507 | 59.967 | 2 | 4 | 2.3375 | 244 |
| January validation (group split) | all | first 512 tokens | 8718 | 30.707 | 0 | 4 | 0.8633 | 45 |
| January validation (group split) | all | whole report | 8718 | 60.186 | 4 | 4 | 3.0574 | 104 |
| January validation (group split) | malware | first 512 tokens | 5557 | 41.659 | 0 | 4 | 1.1650 | 45 |
| January validation (group split) | malware | whole report | 5557 | 61.616 | 4 | 4 | 3.4378 | 45 |
| January validation (group split) | benign | first 512 tokens | 3161 | 11.452 | 0 | 3 | 0.3328 | 11 |
| January validation (group split) | benign | whole report | 3161 | 57.672 | 2 | 4 | 2.3885 | 104 |
| April | all | first 512 tokens | 17402 | 21.653 | 0 | 2 | 0.6485 | 28 |
| April | all | whole report | 17402 | 63.993 | 4 | 4 | 2.6293 | 104 |
| April | malware | first 512 tokens | 9399 | 30.365 | 0 | 2 | 0.8628 | 28 |
| April | malware | whole report | 9399 | 67.348 | 4 | 4 | 2.9483 | 93 |
| April | benign | first 512 tokens | 8003 | 11.421 | 0 | 4 | 0.3970 | 21 |
| April | benign | whole report | 8003 | 60.052 | 2 | 4 | 2.2547 | 104 |

**Decision rule (any population, either scope, class 'all': share > 1% or median > 0): FIX PLANNED (not run), merged into P3.**  Triggers: January training (group split) / first 512 tokens: share 32.836%, median 0; January training (group split) / whole report: share 66.679%, median 4; January validation (group split) / first 512 tokens: share 30.707%, median 0; January validation (group split) / whole report: share 60.186%, median 4; April / first 512 tokens: share 21.653%, median 0; April / whole report: share 63.993%, median 4
