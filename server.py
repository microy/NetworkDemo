#!/usr/bin/env python
# -*- coding: utf-8 -*-


#
# Server side of the NetworkDemo application
#


#
# External dependencies
#
import socket
import sys
import threading
import time


#
# Thread to compute the position of the ball
#
class Ball( threading.Thread ) :
	
	#
	# Initialization
	#
	def __init__( self, clients ) :

		# Initialize the thread
		threading.Thread.__init__( self )

		# Register the client list
		self.clients = clients

	#
	# Thread main loop
	#
	def run( self ) :
		
		self.running = True

		# Screen size
		sw = 1920
		sh = 1200

		# Ball coordinates and speed
		x, y, v, dx, dv = 50, 50, 0, 12, 5

		# Border
		sh = sh - 100 - 30

		# Thread running
		while self.running :

			# Horizontal move
			if x > len(self.clients)*sw or x < 0 :     # rebond sur les parois latérales :
				dx = -dx             # on inverse le déplacement
			x = x + dx

			# Vertical speed variation
			v = v + dv

			# Vertical move
			y = y + v 
			if y > sh :              # niveau du sol à 240 pixels : 
				y = sh             #  défense d'aller + loin !
				v = -v               # rebond : la vitesse s'inverse

			# Send ball coordinates to the clients
			for n, client in enumerate( self.clients ) :
				
			#	print( 'Coordonnées ({},{}) envoyées à {}:{}'.format( x, y, *chost ) )

				# Send the coordinates
				try : client.connection.send( '{},{}.\n'.format( x-n*sw, y ) )
				
				# Client isn't here anymore
				except :
					print( 'Connection lost with {}:{}...'.format( client.address, client.port ) )
					client.connection.close()
					self.clients.remove( client )

			# No more clients
			if not self.clients : break
				
			# Timer
			time.sleep( 0.03 )


#
# Client informations
#
class Client( object ) :
	
	#
	# Initialization
	#
	def __init__( self, address, port, connection ) :
		
		# IP address
		self.address = address
		
		# TCP port
		self.port = port
		
		# Network socket
		self.connection = connection
		
	

# Set up Internet TCP socket
server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
server.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

# Bind socket to port 10000
server.bind( ( '', 10000 ) )

# Start listening for contacts from clients
server.listen( 16 )

# Client list
clients = []

# Required client number
N = 2

# Client connection
while len( clients ) < N :
	
	clnt, ap = server.accept()
	address, port = clnt.getpeername()
	print( 'Connection from {}:{}...'.format( address, port ) )
	clients.append( Client( address, port, clnt ) )

# Close the server
server.close()

# Ball thread
try :
	# Ball thread
	ball_thread = Ball( clients )
	ball_thread.start()
except :
	ball_thread.running = False
	ball_thread.join()
	for client in clients :
		client.close()
		clients.remove( client )
