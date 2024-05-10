from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import os 
from dotenv import load_dotenv
load_dotenv()
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


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
    
    
    
if __name__ == "__main__":
    app.run(debug=True)
    
    
