from flask import Blueprint, request, jsonify

from divbrowse.brapi.v2.allelematrix import BrapiAllelematrix
from divbrowse.brapi.v2.variants import BrapiVariants


def get_brapi_blueprint(config, gd, ad):

    brapi_blueprint = Blueprint('brapi', __name__)

    @brapi_blueprint.route("/serverinfo", methods = ['GET', 'OPTIONS'])
    def __serverinfo():

        serverinfo = config.get('brapi', {}).get('serverinfo', {})

        server_name = serverinfo.get('server_name', None)
        server_description = serverinfo.get('server_description', None)
        organization_name = serverinfo.get('organization_name', None)
        organization_url = serverinfo.get('organization_url', None)
        location = serverinfo.get('location', None)
        contact_email = serverinfo.get('contact_email', None)
        documentation_url = serverinfo.get('documentation_url', None)

        output = {
            "@context": [
                "https://brapi.org/jsonld/context/metadata.jsonld"
            ],
            "metadata": {
                "datafiles": [],
                "pagination": None,
                "status": [
                    {
                        "message": "Request accepted, response successful",
                        "messageType": "INFO"
                    }
                ]
            },
            "result": {
                "calls": [
                    {
                        "contentTypes": ["application/json"],
                        "dataTypes": ["application/json"],
                        "methods": ["GET",],
                        "service": "serverinfo",
                        "versions": ["2.1"]
                    },
                    {
                        "contentTypes": ["application/json"],
                        "dataTypes": ["application/json"],
                        "methods": ["GET",],
                        "service": "commoncropnames",
                        "versions": ["2.1"]
                    },
                    {
                        "contentTypes": ["application/json"],
                        "dataTypes": ["application/json"],
                        "methods": ["GET",],
                        "service": "variants",
                        "versions": ["2.1"]
                    },
                    {
                        "contentTypes": ["application/json"],
                        "dataTypes": ["application/json"],
                        "methods": ["GET",],
                        "service": "allelematrix",
                        "versions": ["2.1"]
                    }
                ],
                "contactEmail": contact_email,
                "documentationURL": documentation_url,
                "location": location,
                "organizationName": organization_name,
                "organizationURL": organization_url,
                "serverDescription": server_description,
                "serverName": server_name
            }
        }

        return jsonify(output)



    @brapi_blueprint.route("/commoncropnames", methods = ['GET', 'OPTIONS'])
    def __commoncropnames():

        commoncropname = config.get('brapi', {}).get('commoncropname', 'unknown')

        output = {
            "@context": [
                "https://brapi.org/jsonld/context/metadata.jsonld"
            ],
            "metadata": {
                "datafiles": [],
                "pagination": {
                    "currentPage": 0,
                    "pageSize": 1000,
                    "totalCount": 1,
                    "totalPages": 1
                },
                "status": [
                    {
                        "message": "Request accepted, response successful",
                        "messageType": "INFO"
                    }
                ]
            },
            "result": {
                "data": [commoncropname]
            }
        }
        return jsonify(output)



    @brapi_blueprint.route("/variants", methods = ['GET', 'OPTIONS'])
    def __variants():
        if request.method == 'GET':
            pass

        else:
            #raise ApiError('Method not allowed', status_code=405)
            return ''

        brapi_variants = BrapiVariants(gd, request)

        return jsonify(brapi_variants.get_response_object())



    @brapi_blueprint.route("/allelematrix", methods = ['GET', 'OPTIONS'])
    def __allelematrix():

        if request.method == 'GET':
            pass

        else:
            #raise ApiError('Method not allowed', status_code=405)
            return ''

        brapi_allelematrix = BrapiAllelematrix(gd, request)

        return jsonify(brapi_allelematrix.get_response_object())



    return brapi_blueprint