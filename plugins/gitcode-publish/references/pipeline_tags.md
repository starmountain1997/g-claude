# model_type → pipeline_tag 映射表

从 transformers `AutoConfig` 的 `model_type` 字段映射到 HuggingFace `pipeline_tag`。

## 文本生成 (text-generation)

适用于纯文本 LLM（自回归语言模型）：

`llama` `qwen2` `qwen2_moe` `mistral` `mixtral` `gpt2` `gpt_neox` `gptj` `falcon` `falcon_mamba` `gemma` `gemma2` `gemma3` `phi` `phi3` `bloom` `opt` `gpt_bigcode` `codegen` `stablelm` `mpt` `baichuan` `chatglm` `internlm` `internlm2` `yi` `deepseek` `deepseek_v2` `deepseek_v3` `cohere` `dbrx` `olmo` `olmoe` `command_r` `dolly` `open_llama` `xverse` `minicpm` `qwen` `starcoder2` `exaone` `arctic` `jamba` `nemotron` `mamba` `mamba2` `recurrent_gemma` `persimmon` `granite` `granitemoe`

## 多模态图文 (image-text-to-text)

支持图像输入+文本输出的视觉语言模型：

`qwen2_vl` `qwen2_5_vl` `llava` `llava_next` `llava_next_video` `llava_onevision` `phi3_v` `paligemma` `idefics2` `idefics3` `fuyu` `pixtral` `internvl` `internvl2` `deepseek_vl` `deepseek_vl2` `glm4v` `cogvlm` `minicpmv` `minicpmo` `aria` `emu3` `florence2` `got_ocr2`

## 图像转文本 (image-to-text)

单一图像输入、文本输出（图像描述等）：

`vit_gpt2` `blip` `blip_2` `git` `pix2struct` `vision_encoder_decoder` `trocr` `nougat` `donut`

## 语音识别 (automatic-speech-recognition)

`whisper` `wav2vec2` `hubert` `sew` `sew_d` `unispeech` `unispeech_sat` `wavlm` `data2vec_audio` `wav2vec2_conformer` `wav2vec2_bert` `qwen2_audio_encoder`

## 掩码填充 (fill-mask)

BERT 系编码器模型：

`bert` `roberta` `distilbert` `albert` `electra` `camembert` `xlm_roberta` `megatron_bert` `deberta` `deberta_v2` `mpnet` `squeezebert` `mobilebert` `xlm` `flaubert` `ibert` `luke` `xmod` `nomic_bert`

## 文本到文本生成 (text2text-generation)

Encoder-decoder 模型：

`t5` `bart` `pegasus` `m2m_100` `mt5` `umt5` `led` `blenderbot` `blenderbot_small` `longt5` `switch_transformers` `fsmt`

## 图像分类 (image-classification)

`vit` `convnext` `convnextv2` `swin` `deit` `beit` `regnet` `resnet` `efficientnet` `mobilenet_v1` `mobilenet_v2` `cvt` `levit` `dino_v2`

## 图像分割 (image-segmentation)

`mask2former` `oneformer` `segformer` `detr` (with segmentation head)

## 物体检测 (object-detection)

`detr` `rt_detr` `yolos` `conditional_detr` `deformable_detr` `dab_detr` `deta` `grounding_dino`

## 视觉问答 (visual-question-answering)

使用 `blip_2` `git` 等模型的 VQA 变体时

## 零样本图像分类 (zero-shot-image-classification)

`clip` `siglip` `altclip` `groupvit` `blip` `chinese_clip` `eva`

## 零样本物体检测 (zero-shot-object-detection)

`owlvit` `owlv2` `grounding_dino`

## 音频分类 (audio-classification)

`wav2vec2` (带分类头) `hubert` `audio_spectrogram_transformer` `clap` `unispeech_sat`

## 语音合成 (text-to-speech)

`speecht5` `bark` `vits`

## 文本转音频 (text-to-audio)

`audioldm` `audioldm2` `musicgen` `musicgen_melody`

## 深度估计 (depth-estimation)

`dpt` `depth_anything` `depth_pro` `glpn` `zoedepth`

## 文档问答 (document-question-answering)

`layoutlm` `layoutlmv2` `layoutlmv3` `donut` `layoutxlm`

## 视频分类 (video-classification)

`timesformer` `videomae` `vivit`

## 关键点检测 (keypoint-detection)

`superglue`

______________________________________________________________________

## 推断优先级

1. 精确匹配 `model_type` → 使用上表
1. 如果 `model_type` 不在表中：
   - 包含 `vl` 或以 `_vl` 结尾 → 可能是 `image-text-to-text`
   - 模型名含 `llava`/`vision`/`vlm` → `image-text-to-text`
   - 含 `audio`/`speech`/`whisper` → `automatic-speech-recognition`
   - BERT 系列（`bert`/`roberta`/`electra`）→ `fill-mask`
   - 默认 → 询问用户
1. 如果 config 中 `architectures` 字段提供了更多线索，结合判断
