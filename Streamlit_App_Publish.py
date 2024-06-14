import streamlit as st
import googlemaps
import openai
import urllib.parse

def get_travel_locations(user_input, openai_api_key):
    context = """You are a travel expert specializing in advising on the best places to visit in various regions. You provide recommendations for 
                 destinations accessible by car or suitable for trekking. 
                 Understand the location where the user is asking about along with the number of
                 destinations. 
                 The output should consist of the number of places that the user is asked in that particular regian/area/city/state/country.
                 Make sure you return the exact number of destinations asked
                 The output will be the name of the place, state in which it is present, and the country followed by a comma. 
                 Each destination will be separated by a full stop. 
                 Make sure that you always follow the exact pattern of output and include the name of the location that is given by the user in the output.
                 Do not give any other unnecessary information in the output and stick to providing locations asked by the user.
                 If the user requests a particular destination or multiple then just return those with complete proper format."""
    try:
        openai.api_key = openai_api_key
        conversation = [
            {"role": "system", "content": context},
            {"role": "user", "content": user_input}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation,
            temperature=0.5,
            max_tokens=250
        )
        response_text = response.choices[0].message['content'].strip()
        places = [line.strip() for line in response_text.split('.') if line.strip()]  # Adjusted to handle missing '. ' split issue
        return places, None
    except openai.error.AuthenticationError:
        return None, "OpenAI API Key is invalid or missing."
    except Exception as e:
        return None, f"An error occurred: {str(e)}"


def create_embed_map(api_key, destinations, mode='driving'):
    
    if not destinations:
        return None, "Error: No destinations provided"
    try:
        gmaps = googlemaps.Client(key=api_key)
        geocoded_destinations = []
        for destination in destinations:
            geocode_result = gmaps.geocode(destination)
            if geocode_result:
                geocoded_destinations.append(geocode_result[0]['geometry']['location'])
            else:
                return None, f"Geocode failure: No results returned for {destination}"
        if len(geocoded_destinations) == 1:
            center = f"{geocoded_destinations[0]['lat']},{geocoded_destinations[0]['lng']}"
            embed_url = f"https://www.google.com/maps/embed/v1/view?key={api_key}&center={center}&zoom=15"
        else:
            origin = urllib.parse.quote_plus(destinations[0])
            destination = urllib.parse.quote_plus(destinations[-1])
            waypoints = '|'.join(urllib.parse.quote_plus(dest) for dest in destinations[1:-1])
            waypoints_param = f"&waypoints={waypoints}" if waypoints else ""
            embed_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}{waypoints_param}&mode={mode}"
        return embed_url, None
    except Exception as e:
        return None, str(e)


def create_gpt_user_input(places):
    if not places:
        return "Error: No places provided."
    places_text = ', '.join(places[:-1]) + ', and ' + places[-1] if len(places) > 1 else places[0]
    return f"I want information about these places: {places_text}."


def get_travel_information(user_input, openai_api_key):
    openai.api_key = openai_api_key

    context = """You are a travel expert specializing in providing information about different places especially the tourist spots across the world. 
                 Your goal is to give information about each place that is asked to you by the user.
                 The information should be something that a tourist would want to know.
                 Give four bullet points for each location and each point should not exceed forty words.
                 The first point will have a more detailed address like which exact area does it comes under and the street and the a nearby landmark if there is one.
                 The second point should tell you what is the interesting about the place and what can you enjoy over here and highlight what makes the place unique 
                 and describe the enjoyable experiences available. Use descriptive and appealing language to bring the place to life.
                 The third point should discuss Discuss the ideal duration for a visit, emphasizing how this place can be a memorable part of a day or longer with friends and family. 
                 The fourth point should talk about the working hours for the place for weekdays and weekend and what is the best time to visit the place.
                 Use enthusiastic language to suggest the joy and fulfillment of spending time there.
                 Ensure that your responses are rich with excitement and tailored to spark the interest of tourists. Do not include any superfluous information. 
                 Each point should inspire and motivate the tourist to explore these locations.
                 Make sure you do this for all the places and follow the format accurately.
                 Do not give any other unnecessary information which will not be helful to the tourist."""

    try:
        openai.api_key = openai_api_key
        conversation = [{"role": "system", "content": context}, {"role": "user", "content": user_input}]
        response = openai.ChatCompletion.create(model="gpt-4", messages=conversation, temperature=0.5, max_tokens=3000)
        response_text = response.choices[0].message['content'].strip()
        return response_text, None
    except Exception as e:
        return None, f"An error occurred: {str(e)}"
    


def validate_api_keys(gmaps_api_key, gpt_api_key):
    errors = []
    if not gmaps_api_key:
        errors.append("Google Maps API Key is invalid.")
    if not gpt_api_key:
        errors.append("OpenAI API Key is invalid.")
    return errors


def main():
    st.set_page_config(page_title="Travel Assistant", layout="wide")
    st.title("Travel Assistant")
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    with st.sidebar:
        st.markdown("""
        <style>
        input[type="text"], input[type="password"], textarea {
            height: 34px;
            font-size: 18px;
            width: 300px;
        }
        .stSidebar > div:first-child {
            width: 100%;
        }
        </style>
        <div style="color: red; font-size: 22px; font-weight: bold;">API Keys</div>
        """, unsafe_allow_html=True)
        gmaps_api_key = st.text_input("Google Maps API Key", type="password", key="gmaps_key")
        gpt_api_key = st.text_input("OpenAI API Key", type="password", key="gpt_key")
        st.markdown("<div style='color: red; font-size: 22px; font-weight: bold;'>What do you plan to see?</div>", unsafe_allow_html=True)
        user_input = st.text_area("Ask me about some place...", "", height=80, key="1")
        travel_mode = st.radio("Select your preferred mode of travel:", ('Driving', 'Walking'), index=0)
        
        if st.button('Get Recommendations'):
            errors = validate_api_keys(gmaps_api_key, gpt_api_key)
            if not errors:
                places, place_error = get_travel_locations(user_input, gpt_api_key)
                if place_error:
                    st.error(place_error)
                elif places:
                    st.session_state.places = places
                    st.session_state.places_output = "\n".join(f"{i+1}. {place.split(',')[0]}" for i, place in enumerate(places))
                    map_url, map_error = create_embed_map(gmaps_api_key, places, mode=travel_mode.lower())
                    if map_error:
                        st.error(map_error)
                    else:
                        st.session_state.map_url = map_url
                    user_input_text = create_gpt_user_input(places)
                    travel_info, travel_info_error = get_travel_information(user_input_text, gpt_api_key)
                    if travel_info_error:
                        st.error(travel_info_error)
                    else:
                        st.session_state.travel_info = travel_info
                    st.session_state.page = 'map'
            else:
                st.error("Please check your API keys:\n" + "\n".join(errors))

    if st.session_state.page == 'home':
        st.write("Welcome to the Travel Assistant. Use the sidebar to start!")
    elif st.session_state.page == 'map':
        if st.session_state.map_url:
            st.markdown(f'<iframe src="{st.session_state.map_url}" width="90%" height="600" frameborder="0" style="border:0" allowfullscreen></iframe>', unsafe_allow_html=True)
        if st.button('Get Detailed Information'):
            st.session_state.page = 'details'
    elif st.session_state.page == 'details':
        st.write(st.session_state.travel_info)
        if st.button('Go Back'):
            st.session_state.page = 'map'

    if 'places_output' in st.session_state:
        st.sidebar.write("Locations Suggested are:")
        st.sidebar.write(st.session_state.places_output)

if __name__ == "__main__":
    main()

