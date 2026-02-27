        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            timeout=60.0  # Float, um TypeError zu vermeiden
        )
        
        prompt = f"""Du bist der beste Content-Repurposer der Welt (Grok-Stil: witzig, direkt, viral).
Inhalt: {content}

Erstelle exakt diese Formate:
{chr(10).join('- ' + f for f in formats)}

Jedes Format mit klarer Überschrift trennen."""

        response = client.chat.completions.create(
            model="grok",  # Standard-Model, vermeidet 'not found'
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content
