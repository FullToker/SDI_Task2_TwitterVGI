# SDI_Task2_TwitterVGI

## Project Overview

This project focuses on analyzing Twitter data for Volunteered Geographic Information (VGI) research, specifically examining two major sporting events: the 2017 UEFA Champions League Final and Wimbledon 2017. The project implements multiple sentiment analysis approaches including traditional machine learning models and modern Large Language Models (LLMs) to compare their effectiveness in processing social media data.

## Key Features

- **Multi-event Twitter Data Processing**: Handles large-scale JSON Twitter datasets for UEFA Champions League 2017 and Wimbledon 2017 tournaments
- **Geospatial Analysis**: Extracts and processes geographic coordinates and location information from tweets
- **Sentiment Analysis Comparison**: Implements multiple sentiment analysis methods:
  - BERT-based models (DistilBERT SST-2)
  - OpenAI GPT-4 API integration
  - Traditional keyword-based filtering
- **Multi-language Support**: Processes tweets in multiple languages with translation capabilities
- **Interactive Data Visualization**: Web-based interface for exploring tweet data and analysis results

## Project Structure

```
SDI_Task2_TwitterVGI/
├── Load_Pre/              # Data preprocessing and loading modules
│   ├── data/             # Processed datasets (UEFA, Tennis/Wimbledon)
│   ├── read_Large_json.py # Main Twitter JSON processor
│   ├── time_format.py    # Date/time formatting utilities
│   ├── Sent_ana.ipynb    # Sentiment analysis notebook
│   └── geocsv_pre.ipynb  # Geocoding and CSV preprocessing
├── Eval_llm/             # LLM evaluation and comparison
│   ├── first_eval.ipynb  # ChatGPT vs traditional methods comparison
│   └── eurovision_analysis_*.csv # Analysis results
├── Show_data/            # Web visualization interface
│   ├── tweet_analyzer.html # Interactive tweet analysis dashboard
│   ├── visual_json.ipynb # Data visualization notebook
│   └── supporting JS/CSS files
└── src/                  # Generated plots and statistics
```

## Datasets

The project analyzes two major sporting events:

1. **UEFA Champions League Final 2017** (Real Madrid vs Juventus, Cardiff)
   - Date range: June 1-4, 2017
   - Keywords: UEFA, Champions League, Real Madrid, Juventus, Cardiff, player names
   - Results: ~40k+ relevant tweets processed

2. **Wimbledon 2017** (Tennis Championship)
   - Date range: July 14-18, 2017  
   - Keywords: Wimbledon, Federer, Cilic, tennis-related terms
   - Results: ~10k+ relevant tweets processed

## Technical Implementation

### Data Processing Pipeline

1. **Raw Data Ingestion**: Processes large JSON files (40M+ tweets) using streaming JSON parser
2. **Temporal Filtering**: Filters tweets based on specific date ranges for each event
3. **Topic Filtering**: Uses keyword matching to identify event-relevant tweets
4. **Geographic Processing**: Extracts coordinates and location information
5. **Language Processing**: Handles multilingual content with translation support

### Sentiment Analysis Methods

#### Traditional ML Approach
- **BERT-based**: DistilBERT fine-tuned on SST-2 dataset
- **Confidence Thresholding**: Implements 3-class sentiment (positive/negative/neutral) with confidence scores
- **Processing Speed**: ~0.0001 seconds per tweet

#### LLM Approach  
- **OpenAI GPT-4**: Advanced context understanding and reasoning
- **Structured Output**: JSON-formatted analysis with confidence scores, keywords, and reasoning
- **Processing Speed**: ~2-4 seconds per tweet
- **Token Usage**: ~200-400 tokens per tweet

### Performance Comparison

| Method | Speed | Accuracy | Cost | Context Understanding |
|--------|-------|----------|------|--------------------|
| BERT | Very Fast | Good | Low | Limited |
| GPT-4 | Slow | Excellent | High | Superior |

## Key Findings

- **Method Agreement**: Traditional and LLM approaches show ~70-80% agreement on binary classification
- **Cost-Performance Trade-off**: LLM methods are 10,000x slower and significantly more expensive but provide richer analysis
- **Geographic Distribution**: Strong clustering around event locations (UK for Wimbledon, Cardiff/Madrid for UEFA)
- **Temporal Patterns**: Clear sentiment shifts before/during/after major events

## Installation & Usage

### Prerequisites
```bash
pip install pandas numpy transformers torch openai ijson
```

### Basic Usage

1. **Process Twitter JSON data**:
```bash
python Load_Pre/read_Large_json.py input.json output.csv output_detailed.json
```

2. **Run sentiment analysis**:
```bash
jupyter notebook Load_Pre/Sent_ana.ipynb
```

3. **Compare LLM vs traditional methods**:
```bash
jupyter notebook Eval_llm/first_eval.ipynb
```

4. **Visualize results**:
Open `Show_data/tweet_analyzer.html` in a web browser

## Research Applications

This project demonstrates practical applications in:
- **Crisis Informatics**: Real-time event monitoring through social media
- **Digital Geography**: Understanding spatial patterns in social media discourse  
- **Computational Social Science**: Comparing automated content analysis methods
- **Sports Analytics**: Fan sentiment and engagement analysis during major events

## Future Work

- Integration of more advanced geospatial analysis
- Real-time streaming data processing
- Additional LLM model comparisons (Claude, Gemini)
- Enhanced multilingual support
- Scalability improvements for larger datasets

## License

This project is developed for academic research purposes as part of SDI (Spatial Data Infrastructure) coursework.
