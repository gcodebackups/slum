#
# nodeFactory - a class used to register new maya nodes based on slum templates.
#
#    Copyright (C) 2008 - Roberto Hradec
#
# ---------------------------------------------------------------------------
#	 This file is part of SLUM.
#
#    SLUM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    SLUM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with SLUM.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------------

import copy
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaRender as OpenMayaRender
from shaderBase import *
from shaderSurface import *
from shaderLight import *
from glob import glob
import os,sys
import slum

userClassify = {
	'surface' 		: 'shader/surface',
	'displacement' 	: 'shader/displacement',
	'float' 		: 'utility/general',
	'color' 		: 'utility/color',
	'light' 		: 'light',
}

class swatchRender(OpenMayaRender.MSwatchRenderBase):
	def __init__(self, mobj, mobjRender, res):
		OpenMayaRender.MSwatchRenderBase(self, mobj, mobjRender, res)
		print mobj, mobjRender, res
		pass
	def doIteration (self):
		pass
	def swatchNode (self):
		#returns the node for which the swatch is required to be generated
		pass
	def node (self):
		#returns the node used to compute the swatch
		pass
	def resolution (self):
		#returns the expected resolution of the swatch image
		pass
	def image (self):
		# returns the swatch image
		pass
	def createObj(self):
		pass


class nodeFactory:
	def __init__(self, mplugin, pluginName, PluginNodeId, searchPath = ['SLUM_SEARCH_PATH', 'MAYA_SCRIPT_PATH', 'PYTHONPATH'] ):
		# call generic slum code to find installed classes
		self.classes 		= slum.collectSlumClasses( searchPath = searchPath ).allClasses
		self.mplugin 		= mplugin
		self.pluginName 	= pluginName
		self.PluginNodeId 	= PluginNodeId
		self.searchPath 	= searchPath
		self.callbackIDs 	= []

	def register(self):
		'''
			loop trough all gathered slum classes and register a new node type for each one
		'''
		xxx = OpenMayaUI.MHWShaderSwatchGenerator.initialize()
		for classe in self.classes.keys():

			nodeTypeName			= 'slum_%s' % classe
			#try:
			#	nodeType 			= OpenMayaMPx.MPxNode.kHardwareShader
			#except:
			#	nodeType 			= OpenMayaMPx.MPxNode.kHwShaderNode
			nodeType 		= OpenMayaMPx.MPxNode.kHwShaderNode
			nodeCreator 		= shaderSurface.nodeCreator
			nodeInitializer 	= shaderSurface.nodeInitializer
			nodeInitializeCallback 	= shaderSurface.slumInitializer


			# Don't initialize swatches in batch mode
			if OpenMaya.MGlobal.mayaState() != OpenMaya.MGlobal.kBatch:
					swatchName = "%sRenderSwatchGen" % nodeTypeName
					#x = copy.deepcopy(OpenMayaUI.MHWShaderSwatchGenerator.createObj)
					#OpenMayaRender.MSwatchRenderRegister.registerSwatchRender(swatchName, swatchRender.createObj )
					swatchName = "/:swatch/%s" % swatchName
					#print swatchName


#_0849aa18_p_MString ['__class__', '__cmp__', '__delattr__', '__doc__', '__getattribute__', '__hash__', '__hex__', '__init__', '__int__', '__long__', '__new__', '__oct__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__str__', 'acquire', 'append', 'disown', 'next', 'own']
#<Swig Object of type 'MString *' at 0x18aa4908>

			#swatchName 				= ''
			#swatchName 				= "/:swatch/%s" %  OpenMayaUI.MHWShaderSwatchGenerator.initialize()
			#xxx = OpenMayaUI.MHWShaderSwatchGenerator.initialize()
			#print xxx, dir(xxx)
			#print xxx.__repr__()
			#print xxx.__class__
			#print xxx.next()
			#swatchName = ":swatch/slumSwatch%s" % classe
			#OpenMayaRender.MSwatchRenderRegister.registerSwatchRender(swatchName,
			#			OpenMayaUI.MHWShaderSwatchGenerator.createObj );

			slumShader = slum.evalSlumClass(self.classes[classe]['code'], classe)

			if slumShader.type() == 'light':
				nodeTypeName			= 'slumLight_%s' % classe
				nodeType 				= OpenMayaMPx.MPxNode.kLocatorNode
				nodeCreator 			= shaderLight.nodeCreator
				nodeInitializer 		= shaderLight.nodeInitializer
				nodeInitializeCallback	= shaderLight.slumInitializer
				swatchName 				= ''

			#register a node for the current slum class

			self.mplugin.registerNode(
					nodeTypeName,
					OpenMaya.MTypeId( self.PluginNodeId + slumShader.ID() ),
					nodeCreator,
					nodeInitializer,
					nodeType,
					'%s%s' % (userClassify[ slumShader.type() ], swatchName)
			)
			self.callbackIDs.append(
				OpenMaya.MDGMessage.addNodeAddedCallback ( nodeInitializeCallback, nodeTypeName)
			)
			del slumShader

	def unregister(self):
		for classe in self.classes.keys():
			slumShader = slum.evalSlumClass(self.classes[classe]['code'], classe)
			self.mplugin.deregisterNode( OpenMaya.MTypeId( self.PluginNodeId + slumShader.ID() ) )

		for each in self.callbackIDs:
			removeCallback( each )
