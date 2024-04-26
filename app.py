import pandas as pd
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, jsonify

def getAllMovies():
    movies = pd.read_csv('converted_file.csv')
    return list(movies['title'].str.capitalize())

def fetch_movie_details(movie_title):
    movies_df = pd.read_csv('converted_file.csv')
    movie_data = movies_df[movies_df['title'] == movie_title]
    if movie_data.empty:
      return None
    movie_details = {
        "overview": movie_data.iloc[0]["overview"],
        "title": movie_data.iloc[0]["title"],
    }
    return movie_details

def Recommend(movie):
    
    movies = pd.read_csv('converted_file.csv')
    movie_lower = movie.lower()
    filtered_movies = movies[movies['title'].str.lower() == movie_lower]
    if filtered_movies.empty:
        return []
    cv = CountVectorizer(max_features=5000, stop_words='english')
    countMatrix = cv.fit_transform(movies['tags'])
    similarity = cosine_similarity(countMatrix)
    
    movie_indices = filtered_movies.index  
    movieList = []

    for movie_index in movie_indices:
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:21]
        for i in movies_list:
            recommended_movie_title = movies.iloc[i[0]]['title']
            recommended_movie_details = fetch_movie_details(recommended_movie_title)
            movieList.append(recommended_movie_details)
    return movieList

app = Flask(__name__, static_folder='film-insight-app/build',
            static_url_path='/')
CORS(app)

@app.route('/api/movies', methods=['GET'])
@cross_origin()
def movies():
    movies = getAllMovies()
    result = {'arr': movies}
    return jsonify(result)


@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/similarity/<name>')
@cross_origin()
def similarity(name):
    
    movie = name
    recommendations = Recommend(movie)
    
    if recommendations:
        if isinstance(recommendations[0], dict):
            movieList = [movie_dict['title'] for movie_dict in recommendations]
            movieString = '---'.join(movieList)
            resultArray = movieString.split('---')
            apiResult = {'movies': resultArray}
            return jsonify(apiResult)
        else:
            print("Unexpected data format from Recommend function. Expected list of dictionaries.")
            print("Recommendations:", recommendations)
            return jsonify({'error': 'Unexpected data format from Recommend function'})
    else:
        print("No recommendations found for the movie:", movie)
        return jsonify({'error': 'No recommendations found'})

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
