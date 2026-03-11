import { NextRequest, NextResponse } from 'next/server'

const PYTHON_AGENT_URL = process.env.PYTHON_AGENT_URL || 'http://localhost:5001'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, userId = 'user_001' } = body

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    const response = await fetch(`${PYTHON_AGENT_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, user_id: userId }),
    })

    if (!response.ok) {
      throw new Error(`Python agent error: ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Failed to process message' },
      { status: 500 }
    )
  }
}
