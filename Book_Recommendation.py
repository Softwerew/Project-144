# Streamlit dependencies
import streamlit as st

# Data handling dependencies
import pandas as pd
import numpy as np
#from IPython.core.display import HTML



# Data Loading
books_list = pd.read_csv('books.csv')
# For Coolberative Recommendation
pt=books_list.pivot_table(index='User-ID',columns='Book-Title',values='Book-Rating')
user_similarity = pt.T.corr()



def get_user_similarity(User_id):
    # Pick a user ID

    picked_userid = User_id

    # Remove picked user ID from the user list
    user_similarity.drop(index=picked_userid, inplace=True)

    # Take a look at the data
    return user_similarity


def get_similar_users(picked_userid):
    #Number of similar users
    n = 10

    # User similarity threashold
    user_similarity_threshold = 0.3

    # Get top n similar users
    similar_users = user_similarity[user_similarity[picked_userid]>user_similarity_threshold][picked_userid].sort_values(ascending=False)[:n]

    return similar_users

def read_books_userid(picked_userid):
    # Books that the target user has read
    picked_userid_read = pt[pt.index == picked_userid].dropna(axis=1, how='all')
    return picked_userid_read

def sim_userbooks(similar_users):
    # books that similar users read. Remove books that none of the similar users have read
    similar_user_books = pt[pt.index.isin(similar_users.index)].dropna(axis=1, how='all')
    return similar_user_books

def user_collaborative_recommendation(similar_user_books,similar_users,m):
    # A dictionary to store item scores
    item_score = {}

    # Loop through items
    for i in similar_user_books.columns:
      # Get the ratings for book i
      book_rating = similar_user_books[i]
      # Create a variable to store the score
      total = 0
      # Create a variable to store the number of scores
      count = 0
      # Loop through similar users
      for u in similar_users.index:
        # If the book has rating
        if pd.isna(book_rating[u]) == False:
          # Score is the sum of user similarity score multiply by the book rating
          score = similar_users[u] * book_rating[u]
          # Add the score to the total score for the book so far
          total += score
          # Add 1 to the count
          count +=1
      # Get the average score for the item
      item_score[i] = total / count

    # Convert dictionary to pandas dataframe
    item_score = pd.DataFrame(item_score.items(), columns=['book', 'book_score'])

    # Sort the books by score
    ranked_item_score = item_score.sort_values(by='book_score', ascending=False)

    return ranked_item_score.head(m)
def user_dropped_data(similar_user_books,picked_userid_read):
    # Remove the read book from the book list
    drop_user_books=similar_user_books.drop(picked_userid_read.columns,axis=1, inplace=False, errors='ignore')

    # Take a look at the data
    return drop_user_books

def content_based_recommend(random_sample,results,id, num):
    recs = results[id]
    recommend_books_id = []
    if len(recs) != 0:
        recs = results[id][:num+1]
        for rec in recs:
            if rec[1] != id:
                recommend_books_id.append(rec[1])
        rslt = random_sample.loc[random_sample['ISBN'].isin(recommend_books_id)]
        return rslt[~rslt.duplicated('ISBN')]
    else:
        return []





def path_to_image_html(path):
    return '<img src="'+ path + '" >'
    
def load_DF(df):
    return HTML(df[['Book-Title', 'Book-Author','Year-Of-Publication','Publisher','Image-URL-M']].to_html(formatters={'Image-URL-M': path_to_image_html}, escape=False))





# App declaration
def main():
    # Header contents
    st.write('# Book Recommender Engine')
    # st.image('resources/imgs/Image_header.png',use_column_width=True)
    # Recommender System algorithm selection
    sys = 'Collaborative Based Filtering'
    if sys == 'Collaborative Based Filtering':
         # User-based preferences
        st.write('### Enter Your User ID')
        picked_userid = st.number_input("User ID",step=1,value=254)
        st.write('### Enter Number of Recommendation')
        n = st.number_input("No Of Recommendation",step=1,value=5)
        if st.button("Recommend"):
            try:
                with st.spinner('Loading...'):
                    user_similarity = get_user_similarity(picked_userid)
                    similar_users = get_similar_users(picked_userid)
                    picked_userid_read=read_books_userid(picked_userid)
                    similar_user_books=sim_userbooks(similar_users)
                    drop_user_books=user_dropped_data(similar_user_books,picked_userid_read)
                    recommended_books=user_collaborative_recommendation(drop_user_books,similar_users,n)
                    recommended_books.reset_index(inplace=True)
                    st.title("We think you'll like:")
                    book_title = recommended_books['book'].values
                    book_rating = recommended_books['book_score'].values
                    book_data_df = pd.DataFrame(columns=['Book-Title', 'Book-Author','Year-Of-Publication','Publisher','Image-URL-M'])
                    for i,j in enumerate(book_title):
                       rec_books = books_list[(books_list['Book-Title'] == j)]
                       rst = rec_books.iloc[[0]]
                       book_data_df.loc[i+1] = [rst['Book-Title'].values[0]] + [rst['Book-Author'].values[0]] + [rst['Year-Of-Publication'].values[0]] + [rst['Publisher'].values[0]] + [rst['Image-URL-M'].values[0]]
                    reco_books = load_DF(book_data_df)   
                    reco_books    
                    
            except:
                st.error("Oops! Looks like this algorithm does't work.\
                            We'll need to fix it!")
        

    



if __name__ == '__main__':
    main()
