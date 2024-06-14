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
                 Make sure you retunr the exact number of destinations asked
                 The output will be the name of the place, state in which it is present, and the country followed by a comma. 
                 Each destination will be sepparated by a full stop. 
                 Make sure that you always follow the exact pattern of output and include the name of the location that is given by the user in the output.
                 Do not give any other unnecessary information in the output and stick to providiing locations asked by the user.
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
        places = [line.split('. ')[1].strip() for line in response_text.split('\n') if line.strip()]  # Split by '. ' and strip spaces
        return places
    except openai.error.AuthenticationError:
        return None, "OpenAI API Key is invalid or missing."
    except Exception as e:
        return None, str(e)

def create_embed_map(api_key, destinations, mode='driving'):
    gmaps = googlemaps.Client(key=api_key)
    if not destinations:
        st.error("Error: No destinations provided")
        return None

    # Geocode all destinations to get precise coordinates
    geocoded_destinations = []
    for destination in destinations:
        geocode_result = gmaps.geocode(destination)
        if geocode_result:
            geocoded_destinations.append(geocode_result[0]['geometry']['location'])
        else:
            st.error(f"Geocode failure: No results returned for {destination}")
            return None

    # Create the embed URL based on the number of destinations
    if len(geocoded_destinations) == 1:
        center = f"{geocoded_destinations[0]['lat']},{geocoded_destinations[0]['lng']}"
        embed_url = f"https://www.google.com/maps/embed/v1/view?key={api_key}&center={center}&zoom=15"
    else:
        origin = urllib.parse.quote_plus(destinations[0])
        destination = urllib.parse.quote_plus(destinations[-1])
        waypoints = '|'.join(urllib.parse.quote_plus(dest) for dest in destinations[1:-1])
        waypoints_param = f"&waypoints={waypoints}" if waypoints else ""
        embed_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}{waypoints_param}&mode={mode}"

    return embed_url


def create_gpt_user_input(places):
    if not places:
        return "Error: No places provided."

    # Join the list of places into a single string with proper formatting
    if len(places) == 1:
        places_text = places[0]
    else:
        # Create a comma-separated list, with 'and' before the last place
        places_text = ', '.join(places[:-1]) + ', and ' + places[-1]

    # Create the user input text for the GPT model
    user_input_text = f"I want information about these places: {places_text}."
    return user_input_text


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

    conversation = [
        {"role": "system", "content": context},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation,
            temperature=0.5,  # A slight temperature increase for more varied responses
            max_tokens=3000
        )

        # Extract the text from the response and format it into a list of places
        response_text = response.choices[0].message['content'].strip()
        return response_text
        

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    


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
    # Note: Streamlit currently does not support dynamically changing the sidebar width via API or straightforward CSS.
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    with st.sidebar:
        st.markdown("""
        <style>
        input[type="text"], input[type="password"] {
            height: 34px;
            font-size: 18px;
            width: 100%;    
        }
        /* You may attempt to adjust the sidebar width using this CSS, but it might not work as expected. */
        .css-1d391kg {width: 350px;}
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
                # If no errors, proceed with API operations
                places = get_travel_locations(user_input, gpt_api_key)
                if places:
                    st.session_state.places = places
                    st.session_state.places_output = "\n".join(f"{i+1}. {place.split(',')[0]}" for i, place in enumerate(places))
                    st.session_state.map_url = create_embed_map(gmaps_api_key, places, mode=travel_mode.lower())
                    user_input_text = create_gpt_user_input(places)
                    st.session_state.travel_info = get_travel_information(user_input_text, gpt_api_key)
                    st.session_state.page = 'map'
            else:
                # Display errors on the main screen
                st.error("Please check your API keys:\n" + "\n".join(errors))

    if st.session_state.page == 'home':
        st.write("Welcome to the Travel Assistant. Use the sidebar to start!")
    elif st.session_state.page == 'map':
        if st.session_state.map_url:
            st.markdown(f'<iframe src="{st.session_state.map_url}" width="100%" height="550" frameborder="0" style="border:0" allowfullscreen></iframe>', unsafe_allow_html=True)
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

