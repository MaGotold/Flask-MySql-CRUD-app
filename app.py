from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import os 
from dotenv import load_dotenv
load_dotenv()
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields,ValidationError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)


#Team model
class Team(db.Model):
    """
    Represents a team within a league, storing details about the team's name and league.

    Attributes:
        id (int): Unique identifier for each team, serves as the primary key.
        team_name (str): Name of the team.
        league (str): Name of the league the team participates in.
    """
    
    #define columns for Team model
    id = db.Column(db.Integer, primary_key = True)
    team_name = db.Column(db.String(40))
    league = db.Column(db.String(40))
    
    def save_to_db(self):
        """
        Saves the instance of the Team in database
        
        Returns:
            self (team): The instance of the Team that was saved
        """
        db.session.add(self)
        db.session.commit()
        return self
    
    def __init__(self, team_name, league):
        """Initialize a new team instance
        
        Args:
            team_name (str): The name of the team.
            league (str): The name of league the team plays in"""
        self.team_name = team_name
        self.league = league
    
    #provides human-readable representation of the Team instance for debugging purpose
    def __repr__(self):
        return f"<Team {self.id}>"


with app.app_context():
    db.create_all()


#Schema for the Team model using marshmallow-sqlalchemy
class TeamSchema(SQLAlchemyAutoSchema):
    """
    This schema automatically generates fields based on the Team model and provides
    customization for additional validation and serialization behavior.
    """
    class Meta(SQLAlchemyAutoSchema.Meta):
        #configuring specific options for model
        model = Team
        sqla_session = db.session
        load_instance = True
    
    #fields definition
    id = fields.Number(dump_only = True)
    team_name = fields.String(required = True)
    league = fields.String(required = True)
    
    
@app.route('/teams', methods = ['GET'])
def index():
    """
    Endpoint to retrieve a list of all teams.
    
    Retrieves all teams from the database, serializes them using the TeamSchema,
    and returns the serialized data in JSON format.

    Returns:
        Response: Flask response object with JSON data containing all teams and a 200 HTTP status code.
    """
    get_teams = Team.query.all()
    team_schema = TeamSchema(many = True)
    teams = team_schema.dump(get_teams) 
    return make_response(jsonify({"teams":teams}))


@app.route('/teams/<id>', methods = ['GET'])
def get_team_by_id(id):
    """
    This endpoint retrieves detailed information about a team from the database
    using its unique identifier. It is specifically designed to handle GET requests where
    the id is a mandatory URL parameter.
    
    Parameters:
    id (int): The unique identifier of the team. This ID is used to fetch and update the team record.
    
    Response: Flask response object with JSON data containing team based on id
    """
    get_team = Team.query.get_or_404(id)
    team_schema = TeamSchema()
    team = team_schema.dump(get_team)
    return make_response(jsonify({"team":team}))


@app.route('/teams/<id>', methods = ['PUT'])
def update_team_by_id(id):
    """
    This endpoint updates the information of a team identified by its unique ID with the provided JSON payload.
    It allows modification of specific fields (team_name, league) within the team record.

    Parameters:
    id (int): The unique identifier of the team. This ID is used to fetch and update the team record.

    Response: Returns a Flask response object containing the updated team data in JSON format.
    """
    data = request.get_json()
    get_team = Team.query.get_or_404(id)
    column_to_put = {
        "team_name": lambda data : setattr(get_team, 'team_name', data),
        "league": lambda data : setattr(get_team, "league", data)
    }
    for key,value in data.items():
        if key in column_to_put:
            column_to_put[key](value)
    db.session.add(get_team)
    db.session.commit()
    team_schema = TeamSchema()
    team = team_schema.dump(get_team)
    return make_response(jsonify({"team": team}))
            
            
@app.route('/teams/<id>', methods = ['DELETE'])
def delete_team_by_id(id):
    """
    This endpoint is used to delete a specific team from the database identified by its 
    unique identifier (id). When a DELETE request is made to this endpoint with a valid id, 
    the specified team is removed from the database. If no team exists with the provided id,
    a 404 Not Found error is returned.
    
    Response: The endpoint does not return any content but indicates the success of the operation
    with an HTTP status code.
    """
    get_team = Team.query.get_or_404(id)
    db.session.delete(get_team)
    db.session.commit()
    return make_response("", 204)
    

@app.route('/teams', methods = ['POST'])
def create_team():
    """
    Create a new team instance and store it in the database.

    This endpoint handles POST requests to add new teams. It expects a JSON object
    with the necessary information to create a Team object.JSON data is validated
    and deserialized into a Team instance, which is then saved to the database.

    Returns:
        jsonify: On successful creation, it returns the newly created team data as JSON
                 with a status code of 201 (Created).
        make_response: If the input data fails validation, it returns the error messages
                       as JSON with a status code of 400 (Bad Request).

    Raises:
        ValidationError: An error is raised if the input JSON data does not conform to the 
                         expected schema, including missing required fields or improper data types.
    """
    data = request.get_json()
    team_schema = TeamSchema()
    try: 
        team = team_schema.load(data)    
        result = team_schema.dump(team.save_to_db())
        return make_response(jsonify({"teams": result}))
    except ValidationError as err:
        return make_response(err.messages)
    #add validation for handling unknown fields
    
    
if __name__ == "__main__":
    app.run(debug=True)
    
    
