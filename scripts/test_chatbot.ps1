# Quick chatbot testing script
# Usage: .\scripts\test_chatbot.ps1

$API_URL = "http://127.0.0.1:8081/prompt"

function Send-ChatMessage {
    param(
        [string]$Message,
        [string]$SessionId = ""
    )
    
    $body = @{
        prompt = $Message
    }
    
    if ($SessionId) {
        $body.session_id = $SessionId
    }
    
    $json = $body | ConvertTo-Json
    
    Write-Host "`n💬 YOU: " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
    
    $response = Invoke-RestMethod -Uri $API_URL -Method POST -Body $json -ContentType "application/json"
    
    Write-Host "`n🤖 ASSISTANT:" -ForegroundColor Green
    Write-Host $response.response
    Write-Host "`n📋 Session ID: $($response.session_id)" -ForegroundColor Yellow
    
    return $response.session_id
}

# Test 1: Simple course query
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "TEST 1: Basic Course Query" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
$session = Send-ChatMessage -Message "Show me math courses for UCB"

# Test 2: Follow-up question (same session)
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "TEST 2: Follow-up Question" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
$session = Send-ChatMessage -Message "What about CS courses?" -SessionId $session

# Test 3: Different campus
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "TEST 3: Different Campus" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
$session = Send-ChatMessage -Message "Now show me UCSD courses" -SessionId $session

# Test 4: New session
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "TEST 4: New Session" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Send-ChatMessage -Message "What courses can I take at UC Davis for computer science?"

Write-Host "`n✅ Testing complete!" -ForegroundColor Green
