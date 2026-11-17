| tensor | shape | released: L2 / mean abs | ours (3 folds): L2 / mean abs |
|---|---|---|---|
| `encoder.weight` | [50001, 64] | 106.900 / 0.0506 | 41.189 / 0.0181 ; 40.776 / 0.0180 ; 40.914 / 0.0180 |
| `pos_encoder.pe` | [5000, 1, 64] | 400.000 / 0.6368 | 400.000 / 0.6368 ; 400.000 / 0.6368 ; 400.000 / 0.6368 |
| `transformer_encoder.layers.0.self_attn.in_proj_weight` | [192, 64] | 10.413 / 0.0792 | 10.209 / 0.0786 ; 10.041 / 0.0774 ; 10.072 / 0.0778 |
| `transformer_encoder.layers.0.self_attn.in_proj_bias` | [192] | 0.527 / 0.0218 | 0.215 / 0.0097 ; 0.176 / 0.0081 ; 0.182 / 0.0078 |
| `transformer_encoder.layers.0.self_attn.out_proj.weight` | [64, 64] | 4.653 / 0.0614 | 1.633 / 0.0203 ; 1.538 / 0.0191 ; 1.645 / 0.0205 |
| `transformer_encoder.layers.0.self_attn.out_proj.bias` | [64] | 0.107 / 0.0108 | 0.113 / 0.0111 ; 0.114 / 0.0115 ; 0.140 / 0.0140 |
| `transformer_encoder.layers.0.linear1.weight` | [256, 64] | 9.517 / 0.0630 | 3.344 / 0.0206 ; 3.329 / 0.0206 ; 3.425 / 0.0210 |
| `transformer_encoder.layers.0.linear1.bias` | [256] | 1.100 / 0.0594 | 0.137 / 0.0068 ; 0.145 / 0.0074 ; 0.146 / 0.0075 |
| `transformer_encoder.layers.0.linear2.weight` | [64, 256] | 5.321 / 0.0344 | 3.181 / 0.0198 ; 3.275 / 0.0204 ; 3.313 / 0.0206 |
| `transformer_encoder.layers.0.linear2.bias` | [64] | 0.284 / 0.0304 | 0.088 / 0.0086 ; 0.106 / 0.0105 ; 0.100 / 0.0100 |
| `transformer_encoder.layers.0.norm1.weight` | [64] | 7.746 / 0.9664 | 7.882 / 0.9844 ; 7.846 / 0.9800 ; 7.840 / 0.9793 |
| `transformer_encoder.layers.0.norm1.bias` | [64] | 0.140 / 0.0130 | 0.120 / 0.0108 ; 0.098 / 0.0102 ; 0.085 / 0.0084 |
| `transformer_encoder.layers.0.norm2.weight` | [64] | 7.618 / 0.9505 | 7.811 / 0.9757 ; 7.855 / 0.9813 ; 7.820 / 0.9766 |
| `transformer_encoder.layers.0.norm2.bias` | [64] | 0.228 / 0.0229 | 0.181 / 0.0200 ; 0.173 / 0.0191 ; 0.223 / 0.0249 |
| `transformer_encoder.layers.1.self_attn.in_proj_weight` | [192, 64] | 10.165 / 0.0778 | 10.194 / 0.0784 ; 9.988 / 0.0770 ; 10.135 / 0.0783 |
| `transformer_encoder.layers.1.self_attn.in_proj_bias` | [192] | 0.407 / 0.0165 | 0.233 / 0.0098 ; 0.190 / 0.0080 ; 0.204 / 0.0087 |
| `transformer_encoder.layers.1.self_attn.out_proj.weight` | [64, 64] | 4.477 / 0.0593 | 1.569 / 0.0196 ; 1.563 / 0.0194 ; 1.582 / 0.0198 |
| `transformer_encoder.layers.1.self_attn.out_proj.bias` | [64] | 0.101 / 0.0103 | 0.112 / 0.0106 ; 0.125 / 0.0122 ; 0.132 / 0.0130 |
| `transformer_encoder.layers.1.linear1.weight` | [256, 64] | 9.444 / 0.0626 | 3.717 / 0.0225 ; 3.455 / 0.0213 ; 3.711 / 0.0227 |
| `transformer_encoder.layers.1.linear1.bias` | [256] | 1.083 / 0.0581 | 0.171 / 0.0082 ; 0.190 / 0.0096 ; 0.180 / 0.0093 |
| `transformer_encoder.layers.1.linear2.weight` | [64, 256] | 5.305 / 0.0342 | 3.507 / 0.0218 ; 3.365 / 0.0209 ; 3.530 / 0.0220 |
| `transformer_encoder.layers.1.linear2.bias` | [64] | 0.281 / 0.0294 | 0.124 / 0.0122 ; 0.119 / 0.0113 ; 0.120 / 0.0123 |
| `transformer_encoder.layers.1.norm1.weight` | [64] | 7.683 / 0.9596 | 7.909 / 0.9882 ; 7.917 / 0.9890 ; 7.904 / 0.9875 |
| `transformer_encoder.layers.1.norm1.bias` | [64] | 0.126 / 0.0127 | 0.060 / 0.0060 ; 0.065 / 0.0063 ; 0.048 / 0.0046 |
| `transformer_encoder.layers.1.norm2.weight` | [64] | 7.619 / 0.9517 | 7.962 / 0.9946 ; 7.957 / 0.9942 ; 7.983 / 0.9969 |
| `transformer_encoder.layers.1.norm2.bias` | [64] | 0.185 / 0.0184 | 0.087 / 0.0088 ; 0.107 / 0.0105 ; 0.104 / 0.0105 |
| `classifier_head.0.0.weight` | [64, 32768] | 87.301 / 0.0510 | 38.518 / 0.0211 ; 37.879 / 0.0208 ; 38.119 / 0.0209 |
| `classifier_head.0.0.bias` | [64] | 0.185 / 0.0208 | 0.128 / 0.0128 ; 0.134 / 0.0131 ; 0.107 / 0.0112 |
| `classifier_head.1.weight` | [1, 64] | 0.339 / 0.0385 | 0.221 / 0.0238 ; 0.200 / 0.0208 ; 0.234 / 0.0251 |
| `classifier_head.1.bias` | [1] | 0.032 / 0.0321 | 0.017 / 0.0171 ; 0.045 / 0.0454 ; 0.018 / 0.0182 |
| **total** | 5,717,313 params | L2 424.00 | L2 404.59 ; L2 404.47 ; L2 404.52 |
