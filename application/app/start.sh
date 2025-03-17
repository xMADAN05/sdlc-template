uvicorn main:sdlc_test_backend --reload --port 8002
# http://127.0.0.1:8002/v1/feedback/docs#/

curl -X 'POST' \
  'http://localhost:8002/v1/sdlc-test-gen/generate-tests' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "AC 1: Validate define subjectivities risk action\nGiven I am an Underwriter or Underwriter Assistant and I want to add a subjectivity to a risk\nWhen I open the \"Define Subjectivities\" risk action\nThen I should see an \"Enter Subjectivities\" button.\nAnd the risk action is available after \"Quote\" risk action and before \"Confirm Bind In PAS\".",
  "additional_context": ""
}
'