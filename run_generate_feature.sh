# run generate_feature.py
# [options]<renewfile> <datefile>  <citationFile> <patentidfile> <TrnedFile1> <TrnedFile2>...
# python generate_feature.py \
# /Users/Leon/Documents/Research/Data/USPCMainAssg1981_2006Drug \
# /Users/Leon/Documents/Research/Data/grantDate \
# /Users/Leon/Documents/Research/Data/citation.csv \
# ./patent_id_list.txt \
# ./TopicTrend.csv ./TFIDF_KmeansTrend.csv

python ./code/generate_feature.py \
./meta/USPCMainAssg1981_2006Drug \
./meta/grantDate \
./meta/citation.csv \
./TFIDF_LDA/patent_id_list.txt \
./TFIDF_Kmeans/TFIDF_KmeansTrend350.csv \
./TFIDF_Kmeans/TFIDF_KmeansTrend400.csv \
./TFIDF_Kmeans/TFIDF_KmeansTrend450.csv \
./TFIDF_Kmeans/TFIDF_KmeansTrend500.csv \
./LDA_TopicTrend/150TopicTrend.csv \
./LDA_TopicTrend/200TopicTrend.csv \
./LDA_TopicTrend/250TopicTrend.csv \
./LDA_TopicTrend/300TopicTrend.csv \
./LDA_TopicTrend/350TopicTrend.csv \
./LDA_TopicTrend/400TopicTrend.csv \
./LDA_TopicTrend/450TopicTrend.csv 

