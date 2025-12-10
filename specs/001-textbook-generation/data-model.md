# Data Model: AI-Native Textbook with AI Chatbot

## Entities

### Textbook Content
- **ID**: Unique identifier for the textbook
- **Title**: Name of the textbook
- **Chapters**: Array of chapter objects
- **Version**: Version number for content tracking
- **CreatedAt**: Timestamp of creation
- **UpdatedAt**: Timestamp of last update

### Chapter
- **ID**: Unique identifier for the chapter
- **Title**: Chapter title
- **Content**: Text content of the chapter
- **Order**: Position in the textbook sequence
- **EmbeddingVector**: Vector representation for RAG search
- **Metadata**: Additional information (word count, reading time, etc.)

### AI Query
- **ID**: Unique identifier for the query
- **UserID**: Identifier for the user making the query
- **Question**: The original question text
- **Timestamp**: When the query was made
- **Context**: Selected text context if applicable
- **SessionID**: Identifier for the conversation session

### AI Response
- **ID**: Unique identifier for the response
- **QueryID**: Reference to the original query
- **Answer**: The AI-generated answer text
- **Sources**: List of textbook content references used
- **Confidence**: Confidence level of the response
- **Timestamp**: When the response was generated

### User Session
- **ID**: Unique identifier for the session
- **UserID**: Identifier for the user
- **StartTime**: When the session started
- **LastActivity**: Timestamp of last interaction
- **Preferences**: User preferences (language, personalization settings)
- **Active**: Boolean indicating if session is active

## Relationships

- Textbook Content **contains** multiple Chapters (1 to many)
- Chapter **belongs to** one Textbook Content (many to 1)
- User Session **has many** AI Queries (1 to many)
- AI Query **has one** AI Response (1 to 1)
- AI Response **references** multiple Chapters for sources (many to many through sources)

## Validation Rules

- Textbook content must have at least one chapter
- Chapter titles must be unique within a textbook
- AI queries must be between 10-500 characters
- AI responses must cite at least one source from textbook content
- User session preferences must be validated against available options

## State Transitions

- Textbook Content: Draft → Published → Archived
- Chapter: Draft → Published → Updated → Archived
- AI Query: Pending → Processing → Completed → Archived