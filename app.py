#!/usr/bin/env python3
import sys
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import json
from ldap3 import Server, Connection, ALL
import pymysql.cursors
import cgitb
import cgi
cgitb.enable()
import settings


app = Flask(__name__, static_url_path='/static')
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

####################################################################################
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

class Root(Resource):
	def get(self):
		return app.send_static_file('index.html')




####################################################################################
class SignIn(Resource):
	def post(self):
		if not request.json:
			abort(400)
		parser = reqparse.RequestParser()
		try:
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		try:
			dbConnection = pymysql.connect(
				settings.MYSQL_HOST,
				settings.MYSQL_USER,
				settings.MYSQL_PASSWD,
				settings.MYSQL_DB,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUser'
			sqlArgs = (request_params['username'], )
			cursor = dbConnection.cursor()
			cursor.callproc(sql, sqlArgs)
			rows = cursor.fetchone()
			if rows is None:
				return make_response(jsonify({'status': 'no user account', 'uri': 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT) + '/signup'}), 400)
		except:
			abort(400)

		if request_params['username'] in session:
			response = {'status': 'success', 'user': session['username']}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				session['username'] = request_params['username']
				response = {'status': 'success', 'user': session['username'] }
				responseCode = 201
			except (LDAPException, error_message):
				response = {'status': 'Access denied'}
				responseCode = 403
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	def delete(self):
		if 'username' in session:
			session.pop('username', None)
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

class SignUp(Resource):
	def post(self):
		if not request.json:
			abort(400)
		parser = reqparse.RequestParser()
		try:
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			parser.add_argument('name', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)
		try:
			dbConnection = pymysql.connect(
			    settings.MYSQL_HOST,
                settings.MYSQL_USER,
                settings.MYSQL_PASSWD,
                settings.MYSQL_DB,
                charset='utf8mb4',
                cursorclass= pymysql.cursors.DictCursor)
			sql = 'createUser'
			sqlArgs = (request_params['username'], request_params['name'])
			cursor = dbConnection.cursor()
			cursor.callproc(sql, sqlArgs)
			rows = cursor.fetchall()
			dbConnection.commit()
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		try:
			ldapServer = Server(host=settings.LDAP_HOST)
			ldapConnection = Connection(ldapServer,
				raise_exceptions=True,
				user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
				password = request_params['password'])
			ldapConnection.open()
			ldapConnection.start_tls()
			ldapConnection.bind()
			session['username'] = request_params['username']
			response = {'status': 'success', 'user': session['username'] }
			responseCode = 201
		except (LDAPException, error_message):
			response = {'status': 'Access denied'}
			responseCode = 403
		finally:
			ldapConnection.unbind()
		return make_response(jsonify(response), responseCode)

class Users(Resource):
    def get(self):
        if 'username' in session:
            try:
	            dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
	            sql = 'getUsers'
	            cursor = dbConnection.cursor()
	            cursor.callproc(sql)
	            rows = cursor.fetchall()
            except:
                abort(500)
            finally:
                cursor.close()
                dbConnection.close()
            return make_response(jsonify({'users': rows}), 200)
        else:
            return make_response(jsonify({'status': 'Not Logged in'}), 403)

class User(Resource):
	def get(self, userName):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()
				return make_response(jsonify({'user': rows}), 200)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

	def delete(self, userName):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)
			if session['username'] == userName:
				try:
					dbConnection = pymysql.connect(
		                settings.MYSQL_HOST,
		                settings.MYSQL_USER,
		                settings.MYSQL_PASSWD,
		                settings.MYSQL_DB,
		                charset='utf8mb4',
		                cursorclass= pymysql.cursors.DictCursor)
					sql = 'deleteUser'
					sqlArgs = (userName, )
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					rows = cursor.fetchone()
					dbConnection.commit()
				except:
					abort(500)
				finally:
					cursor.close()
					dbConnection.close()
					session.pop('username', None)
				return make_response(jsonify({'Successfully Deleted User': userName}), 200)
			else:
				return make_response(jsonify({'status': 'Not Logged in'}), 403)

class Rides(Resource):
    def get(self):
        if 'username' in session:
	        try:
	            dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
	            sql = 'getRides'
	            cursor = dbConnection.cursor()
	            cursor.callproc(sql)
	            rows = cursor.fetchall()
	        except:
	            abort(500)
	        finally:
	            cursor.close()
	            dbConnection.close()
	        return make_response(jsonify({'rides': rows}), 200)
        else:
            return make_response(jsonify({'status': 'Not Logged in'}), 403)

class Wanted(Resource):
	def get(self):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getRidesByFlag'
				sqlArgs = (0,)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchall()
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()
				return make_response(jsonify({'rides': rows}), 200)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

class Available(Resource):
	def get(self):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getRidesByFlag'
				sqlArgs = (1,)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchall()
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({'rides': rows}), 200)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

class UserRides(Resource):
	def get(self, userName):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserRides'
				sqlArgs = (userName,)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchall()
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()
				response = {'rides': rows}
				responseCode = 200
				return make_response(jsonify(response), responseCode)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

	def post(self, userName):
		if 'username' in session:
			if session['username'] == userName:
				if not request.json or not 'StartLocation' in request.json:
					abort(400) # bad request
				name = userName
				sLocation = request.json['StartLocation'];
				dTime = request.json['DepartureTime'];
				dest = request.json['Destination'];
				seats = request.json['Seats'];
				flag = request.json['Flag'];
				try:
					dbConnection = pymysql.connect(settings.MYSQL_HOST,
			            settings.MYSQL_USER,
		                settings.MYSQL_PASSWD,
						settings.MYSQL_DB,
						charset='utf8mb4',
						cursorclass= pymysql.cursors.DictCursor)
					sql = 'createUserRide'
					cursor = dbConnection.cursor()
					sqlArgs = (name, sLocation, dTime, dest, seats, flag)
					cursor.callproc(sql,sqlArgs)
					row = cursor.fetchone()
					dbConnection.commit()
				except:
					abort(500)
				finally:
					cursor.close()
					dbConnection.close()
				uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
				uri = uri+'/rides/'+ str(userName)+'/'+str(row['LAST_INSERT_ID()'])
				return make_response(jsonify( { "uri" : uri } ), 201)
			else:
				return make_response(jsonify({'status': 'Permission Denied'}), 403)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

class UserRide(Resource):
	def get(self, userName, rideID):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)

			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserRideByID'
				sqlArgs = (userName, rideID)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'Ride not found'}), 404)
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()
				response = {'Ride' : rows}
				responseCode = 200
			return make_response(jsonify(response), responseCode)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

	def delete(self, userName, rideID):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserRideByID'
				sqlArgs = (userName, rideID)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'Ride not found'}), 404)
			except:
				abort(500)

			if session['username'] == userName:
				try:
					dbConnection = pymysql.connect(
		                settings.MYSQL_HOST,
		                settings.MYSQL_USER,
		                settings.MYSQL_PASSWD,
		                settings.MYSQL_DB,
		                charset='utf8mb4',
		                cursorclass= pymysql.cursors.DictCursor)
					sql = 'removeUserRide'
					sqlArgs = (rideID,)
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					rows = cursor.fetchone()
					dbConnection.commit()
				except:
					abort(500)
				finally:
					cursor.close()
					dbConnection.close()
					response = {'Successfully Deleted Ride' : rideID}
					responseCode = 200
				return make_response(jsonify(response), responseCode)
			else:
				return make_response(jsonify({'status': 'Permission Denied'}), 403)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

	def put(self, userName, rideID):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserRideByID'
				sqlArgs = (userName, rideID)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'Ride not found'}), 404)
			except:
				abort(500)

			if session['username'] == userName:
				if not request.json and request.json.keys().size() == 0:
					abort(400)
				try:
					dbConnection = pymysql.connect(
		                settings.MYSQL_HOST,
		                settings.MYSQL_USER,
		                settings.MYSQL_PASSWD,
		                settings.MYSQL_DB,
		                charset='utf8mb4',
		                cursorclass= pymysql.cursors.DictCursor)
					lst = list(request.json.keys());
					if lst[0] == 'StartLocation':
						sql = 'updateStartLocation'
						sqlArgs = (request.json['StartLocation'], rideID)
					elif lst[0] == 'DepartureTime':
						sql = 'updateDepartureTime'
						sqlArgs = (request.json['DepartureTime'], rideID)
					elif lst[0] == 'Destination':
						sql = 'updateDestination'
						sqlArgs = (request.json['Destination'], rideID)
					elif lst[0] == 'Seats':
						sql = 'updateSeats'
						sqlArgs = (request.json['Seats'], rideID)
					else:
						abort(400)
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					rows = cursor.fetchone()
					dbConnection.commit()
				except:
					abort(500)
				finally:
					cursor.close()
					dbConnection.close()
				uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
				uri = uri+'/rides/'+userName + '/' + str(rideID)
				return make_response(jsonify( { "uri" : uri } ), 201)
			else:
				return make_response(jsonify({'status': 'Permission Denied'}), 403)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

class Passengers(Resource):
	def get(self, userName, rideID):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName,)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserRideByID'
				sqlArgs = (userName, rideID)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'Ride not found'}), 404)
			except:
				abort(500)

			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getRidePassengers'
				sqlArgs = (rideID,)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchall()
				if rows is None:
				    return make_response(jsonify({'Passengers': 'No Passengers'}), 200)
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()
				response = {'passengers': rows}
				responseCode = 200
			return make_response(jsonify(response), responseCode)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

	def post(self, userName, rideID):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserRideByID'
				sqlArgs = (userName, rideID)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'Ride not found'}), 404)
			except:
				abort(500)

			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserRideByID'
				sqlArgs = (userName, rideID)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row.get("seats") > 0:
					sql = 'addPassenger'
					sqlArgs = (rideID, session['username'])
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					dbConnection.commit()
					sql = 'updateSeats'
					sqlArgs = (row.get("seats")-1, rideID)
					cursor.callproc(sql, sqlArgs)
					dbConnection.commit()
				else:
					return make_response(jsonify({'status': 'ride is full'}), 200)
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()
			uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)+'/rides/'+userName + '/'+ str(rideID) + '/passengers'
			return make_response(jsonify( { "uri" : uri } ), 201)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

class SpecificPassenger(Resource):
	def get(self, userName, rideID, userName2):
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserRideByID'
				sqlArgs = (userName, rideID)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'Ride not found'}), 404)
			except:
				abort(500)
			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUser'
				sqlArgs = (userName, )
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				if rows is None:
					return make_response(jsonify({'status': 'User not found'}), 404)
			except:
				abort(500)

			try:
				dbConnection = pymysql.connect(
	                settings.MYSQL_HOST,
	                settings.MYSQL_USER,
	                settings.MYSQL_PASSWD,
	                settings.MYSQL_DB,
	                charset='utf8mb4',
	                cursorclass= pymysql.cursors.DictCursor)
				sql = 'getSpecificPassenger'
				sqlArgs = (userName2, rideID)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchone()
				dbConnection.commit()
			except:
				abort(500)
			finally:
				cursor.close()
				dbConnection.close()
				response = {'Passenger' : rows}
				responseCode = 200
			return make_response(jsonify(response), responseCode)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)

	def delete(self, userName, rideID, userName2):
		if 'username' in session:
			if session['username'] == userName or session['username'] == userName2:
				try:
					dbConnection = pymysql.connect(
		                settings.MYSQL_HOST,
		                settings.MYSQL_USER,
		                settings.MYSQL_PASSWD,
		                settings.MYSQL_DB,
		                charset='utf8mb4',
		                cursorclass= pymysql.cursors.DictCursor)
					sql = 'getUser'
					sqlArgs = (userName,)
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					rows = cursor.fetchone()
					if rows is None:
						return make_response(jsonify({'status': 'User not found'}), 404)
				except:
					abort(500)
				try:
					dbConnection = pymysql.connect(
		                settings.MYSQL_HOST,
		                settings.MYSQL_USER,
		                settings.MYSQL_PASSWD,
		                settings.MYSQL_DB,
		                charset='utf8mb4',
		                cursorclass= pymysql.cursors.DictCursor)
					sql = 'getUserRideByID'
					sqlArgs = (userName, rideID)
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					rows = cursor.fetchone()
					if rows is None:
						return make_response(jsonify({'status': 'Ride not found'}), 404)
				except:
					abort(500)
				try:
					dbConnection = pymysql.connect(
		                settings.MYSQL_HOST,
		                settings.MYSQL_USER,
		                settings.MYSQL_PASSWD,
		                settings.MYSQL_DB,
		                charset='utf8mb4',
		                cursorclass= pymysql.cursors.DictCursor)
					sql = 'getUser'
					sqlArgs = (userName, )
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					rows = cursor.fetchone()
					if rows is None:
						return make_response(jsonify({'status': 'User not found'}), 404)
				except:
					abort(500)

				try:
					dbConnection = pymysql.connect(
		                settings.MYSQL_HOST,
		                settings.MYSQL_USER,
		                settings.MYSQL_PASSWD,
		                settings.MYSQL_DB,
		                charset='utf8mb4',
		                cursorclass= pymysql.cursors.DictCursor)
					sql = 'deleteSpecificPassenger'
					sqlArgs = (userName2, rideID)
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					sql = 'getUserRideByID'
					sqlArgs = (userName, rideID)
					cursor = dbConnection.cursor()
					cursor.callproc(sql, sqlArgs)
					row = cursor.fetchone()
					sql = 'updateSeats'
					sqlArgs = (row.get("seats")+1, rideID)
					cursor.callproc(sql, sqlArgs)
					rows = cursor.fetchone()
					dbConnection.commit()
				except:
					abort(500)
				finally:
					cursor.close()
					dbConnection.close()
					response = {'Successfully Removed Passenger' : userName2}
					responseCode = 200
				return make_response(jsonify(response), responseCode)
			else:
				return make_response(jsonify({'status': 'Permission Denied'}), 403)
		else:
			return make_response(jsonify({'status': 'Not Logged in'}), 403)


####################################################################################
# Identify/create endpoints and endpoint objects
api = Api(app)
api.add_resource(SignIn, '/signin')
api.add_resource(SignUp, '/signup')
api.add_resource(Users, '/users')
api.add_resource(User, '/users/<string:userName>')
api.add_resource(Rides, '/rides')
api.add_resource(Wanted, '/rides/wanted')
api.add_resource(Available, '/rides/available')
api.add_resource(UserRides, '/rides/<string:userName>')
api.add_resource(UserRide, '/rides/<string:userName>/<int:rideID>')
api.add_resource(Passengers, '/rides/<string:userName>/<int:rideID>/passengers')
api.add_resource(SpecificPassenger, '/rides/<string:userName>/<int:rideID>/passengers/<string:userName2>')
api.add_resource(Root,'/')



#############################################################################
if __name__ == "__main__":
	context = ('cert.pem', 'key.pem') # Identify the certificates you've generated.
	app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG, ssl_context=context)
