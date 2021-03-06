# This file defines functions for serialising and deserialising
# allocation requests and responses.

import json

from . import allocator
from .constraints import * # useful for anything which imports this module 
from .group_size_generator import ImpossibleConstraintsError


# General exception to describe any issues which may arise from
# deserialising a JSON-encoded allocation request.
class InvalidRequestError(Exception):
	def __init__(self, request, message):
		self.request = request
		self.message = message


# Extension to JSONEncoder in order to correctly serialise allocation constraints.
# Not needed for the website, but useful as documentation.
class ConstraintEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, BXY):
			return list(obj)
			
		elif isinstance(obj, IntegerCountConstraint):
			obj_dict = {"constr_type": "IntegerCountConstraint"}
			for attr in ("name","field","priority","should_bool","count_bxy","with_bool","value_bxy"):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		elif isinstance(obj, IntegerAverageConstraint):
			obj_dict = {"constr_type": "IntegerAverageConstraint"}
			for attr in ("name","field","priority","should_bool","average_bxy"):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		elif isinstance(obj, IntegerSimilarityConstraint):
			obj_dict = {"constr_type": "IntegerSimilarityConstraint"}
			for attr in ("name","field","priority","similar_bool"):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		elif isinstance(obj, IntegerGlobalAverageConstraint):
			obj_dict = {"constr_type": "IntegerGlobalAverageConstraint"}
			for attr in ("name","field","priority"):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		elif isinstance(obj, OptionCountConstraint):
			obj_dict = {"constr_type": "IntegerCountConstraint"}
			for attr in ("name","field","priority","should_bool","count_bxy","with_bool","selection",candidates):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		elif isinstance(obj, OptionSimilarityConstraint):
			obj_dict = {"constr_type": "SubsetSimilarityConstraint"}
			for attr in ("name","field","priority","similar_bool","candidates"):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		elif isinstance(obj, SubsetCountConstraint):
			obj_dict = {"constr_type": "IntegerCountConstraint"}
			for attr in ("name","field","priority","should_bool","count_bxy","with_bool","selection",candidates):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		elif isinstance(obj, SubsetSimilarityConstraint):
			obj_dict = {"constr_type": "SubsetSimilarityConstraint"}
			for attr in ("name","field","priority","similar_bool","candidates"):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		elif isinstance(obj, BooleanCountConstraint):
			obj_dict = {"constr_type": "BooleanCountConstraint"}
			for attr in ("name","field","priority","should_bool","count_bxy","with_bool"):
				obj_dict[attr] = getattr(obj, attr)
			return obj_dict
		
		else: # fail with TypeError
			return json.JSONEncoder.default(self, obj)


# Capture and build constraints from the result of deserialising a
# JSON-encoded allocation request.
def constraint_hook(obj):
	try:
		if obj.get("constr_type") == "IntegerCountConstraint":
			# name, field, priority, should_bool, count_bxy, with_bool, value_bxy
			count_bxy = BXY(*obj["count_bxy"])
			value_bxy = BXY(*obj["value_bxy"])
			return IntegerCountConstraint(obj["name"], obj["field"], obj["priority"],
				obj["should_bool"], count_bxy, obj["with_bool"], value_bxy)
		
		elif obj.get("constr_type") == "IntegerAverageConstraint":
			# name, field, priority, should_bool, average_bxy
			average_bxy = BXY(*obj["average_bxy"])
			return IntegerAverageConstraint(obj["name"], obj["field"], obj["priority"],
				obj["should_bool"], average_bxy)
		
		elif obj.get("constr_type") == "IntegerSimilarityConstraint":
			# name, field, priority, similar_bool
			return IntegerSimilarityConstraint(obj["name"], obj["field"], obj["priority"],
				obj["similar_bool"])
		
		elif obj.get("constr_type") == "IntegerGlobalAverageConstraint":
			# name, field, priority
			return IntegerGlobalAverageConstraint(obj["name"], obj["field"], obj["priority"])
		
		elif obj.get("constr_type") == "OptionCountConstraint":
			# name, field, priority, should_bool, count_bxy, with_bool, selection, candidates
			count_bxy = BXY(*obj["count_bxy"])
			return OptionCountConstraint(obj["name"], obj["field"], obj["priority"],
				obj["should_bool"], count_bxy, obj["with_bool"], obj["selection"], obj["candidates"])
		
		elif obj.get("constr_type") == "OptionSimilarityConstraint":
			# name, field, priority, similar_bool, candidates
			return OptionSimilarityConstraint(obj["name"], obj["field"], obj["priority"],
				obj["similar_bool"], obj["candidates"])
		
		elif obj.get("constr_type") == "SubsetCountConstraint":
			# name, field, priority, should_bool, count_bxy, with_bool, selection, candidates
			count_bxy = BXY(*obj["count_bxy"])
			return SubsetCountConstraint(obj["name"], obj["field"], obj["priority"],
				obj["should_bool"], count_bxy, obj["with_bool"], obj["selection"], obj["candidates"])
		
		elif obj.get("constr_type") == "SubsetSimilarityConstraint":
			# name, field, priority, similar_bool, candidates
			return SubsetSimilarityConstraint(obj["name"], obj["field"], obj["priority"],
				obj["similar_bool"], obj["candidates"])
		
		elif obj.get("constr_type") == "BooleanCountConstraint":
			# name, field, priority, should_bool, count_bxy, with_bool
			count_bxy = BXY(*obj["count_bxy"])
			return BooleanCountConstraint(obj["name"], obj["field"], obj["priority"],
				obj["should_bool"], count_bxy, obj["with_bool"])
		
		elif obj.get("constr_type") is not None:
			#TODO will break if anything is called "constr_type"
			raise InvalidRequestError(None, "Invalid constraint JSON")
		
		else:
			return obj
		
	except (KeyError, TypeError):
		name = obj.get("name")
		if name is not None:
			raise InvalidRequestError(None, "Invalid JSON for constraint ({})".format(name))
		else:
			raise InvalidRequestError(None, "Invalid constraint JSON")


# Produce the JSON-encoded result of a successful allocation.
def encode_teams(teams):
	return json.dumps({"success":True, "teams":teams})


# Produce the JSON-encoded result of an unsuccessful allocation.
def encode_failure(exception):
	if isinstance(exception, InvalidRequestError):
		reason = exception.message
	elif isinstance(exception, ImpossibleConstraintsError):
		reason = str(exception)
	else:
		reason = "Something happened"
	return json.dumps({"success":False, "reason":reason})


# Build a valid request 
# Not needed for the website, but useful as documentation.
def encode_request(min_size, ideal_size, max_size, constraints, students):
	return json.dumps({
		"min_size":     min_size,
		"ideal_size":   ideal_size,
		"max_size":     max_size,
		"students":     students,
		"constraints":  constraints},
		cls=ConstraintEncoder)


# Decode an allocation request from a user. This function will validate
# That the request has a valid structure and types, though it won't
# attempt to validate the individual constraints.
def decode_request(request):
	try:
		decoded = json.loads(request, object_hook=constraint_hook)
	except json.decoder.JSONDecodeError:
		raise InvalidRequestError(request, "Invalid JSON")
	except InvalidRequestError as error:
		error.request = request
		raise error
	
	if type(decoded) != dict:
		raise InvalidRequestError(request, "Invalid request")
	
	min_size = decoded.get("min_size")
	if min_size is None or type(min_size) != int:
		raise InvalidRequestError(request, "Invalid minimum size")
	
	ideal_size = decoded.get("ideal_size")
	if ideal_size is None or type(ideal_size) != int:
		raise InvalidRequestError(request, "Invalid ideal size")
	
	max_size = decoded.get("max_size")
	if max_size is None or type(max_size) != int:
		raise InvalidRequestError(request, "Invalid maximum size")
	
	students = decoded.get("students")
	if students is None or type(students) != dict:
		raise InvalidRequestError(request, "Invalid student info")
	
	constraints = decoded.get("constraints")
	if constraints is None:
		constraints = []
	elif type(constraints) != list:
		raise InvalidRequestError(request, "Invalid constraint list")
	
	return min_size, ideal_size, max_size, students, constraints


# Validate a single constraint from an allocation, including whether it
# is applicable to the given student data.
def validate_constraint(request, student_info, constraint):
	if not isinstance(constraint, Constraint):
		raise InvalidRequestError(request, "Invalid constraint")
	
	if constraint.field is None:
		return
	
	for info in student_info.values():
		
		if constraint.field not in info:
			raise InvalidRequestError(request, "Constraint ({}) is on a missing student info field ({})".format(constraint.name, constraint.field))
		
		ctype = constraint.constraint_type
		svalue = info[constraint.field]
		
		if ((ctype == "integer" and type(svalue) != int) or
				(ctype == "option" and type(svalue) != str) or
				(ctype == "subset" and (type(svalue) != list or not all(map(lambda x: type(x)==str, svalue)))) or
				(ctype == "boolean" and type(svalue) != bool)):
			raise InvalidRequestError(request, "Constraint ({}) type ({}) doesn't match student info field ({}) type".format(constraint.name, ctype, constraint.field))


# Validate a single row of student data,
# such as whether answers are in the list of valid candidates
def validate_data(request, constraints, student):
	for constraint in constraints:
		if constraint.constraint_type == "integer":
			response = student[constraint.field]
			if type(response) != int:
				raise InvalidRequestError(request, "Student response ({}) is not a valid choice for constraint ({})".format(response, constraint.name))
		elif constraint.constraint_type == "option":
			response = student[constraint.field]
			if response not in constraint.candidates:
					raise InvalidRequestError(request, "Student response ({}) is not a valid choice for constraint ({})".format(response, constraint.name))
		elif constraint.constraint_type == "subset":
			for response in student[constraint.field]:
				if response not in constraint.candidates:
					raise InvalidRequestError(request, "Student response ({}) is not a valid choice for constraint ({})".format(response, constraint.name))
		else:
			#constraint.constraint_type == "boolean":
			response = student[constraint.field]
			if type(response) != bool:
				raise InvalidRequestError(request, "Student response ({}) is not a valid choice for constraint ({})".format(response, constraint.name))


# Validate an allocation request from the user, including constraints and student information
def validate_request(request, min_size, ideal_size, max_size, student_info, constraints): #TODO
	if not min_size <= ideal_size <= max_size:
		raise InvalidRequestError(request, "Invalid group size ordering")
	
	for info in student_info.values():
		if type(info) != dict:
			raise InvalidRequestError(request, "Invalid student data")
	
	for constraint in constraints:
		validate_constraint(request, student_info, constraint)
	
	for info in student_info.values():
		validate_data(request, constraints, info)


# Perform the complete deserialise->allocate->serialise process.
def allocate(request):
	try:
		decoded = decode_request(request)
		validate_request(request, *decoded)
		steps = 10**5 #TODO need to control number of annealing steps
		team_data = allocator.allocate_teams(*decoded, steps=steps, progress=False)
		teams = {id:team for id, team in enumerate(team_data.keys())}
		return encode_teams(teams)
	except Exception as e:
		return encode_failure(e)
