import os
import asyncio
import edge_tts
from pydub import AudioSegment

# -------------------------------------------------------
# Output directory
# -------------------------------------------------------
OUTPUT_DIR = "data/audio_samples/test_speakers"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------
# Available Voices (Microsoft Neural Voices)
# -------------------------------------------------------
VOICES = {
    # Female voices
    'female1': 'en-US-JennyNeural',
    'female2': 'en-US-AriaNeural',
    'female3': 'en-US-SaraNeural',
    'female4': 'en-GB-SoniaNeural',
    
    # Male voices
    'male1': 'en-US-GuyNeural',
    'male2': 'en-US-EricNeural',
    'male3': 'en-US-TonyNeural',
    'male4': 'en-GB-RyanNeural',
    
    # Children voices (higher pitch)
    'child_boy': 'en-US-GuyNeural',  # Will pitch shift
    'child_girl': 'en-US-JennyNeural',  # Will pitch shift
}

# -------------------------------------------------------
# Test Scenarios
# -------------------------------------------------------
SCENARIOS = {
    '1_female_male_female2': {
        'description': '1 Female + 1 Male + 1 Different Female',
        'speakers': [
            {'voice': 'female1', 'text': "Hello everyone, I'm testing the voice analyzer system. Can you all hear me clearly? This is the first speaker."},
            {'voice': 'male1', 'text': "Yes, loud and clear. I'm the second speaker, and I'm male. This technology is really impressive and working well."},
            {'voice': 'female2', 'text': "I agree completely! I'm the third speaker, another female voice. The gender detection seems to be working perfectly now."}
        ]
    },
    
    '2_female_male_male2': {
        'description': '1 Female + 2 Different Males',
        'speakers': [
            {'voice': 'female1', 'text': "Good morning everyone. Let's discuss the project results and review our progress this week. I'll start the meeting."},
            {'voice': 'male1', 'text': "Sounds good. I'm the first male speaker. I think we made excellent progress this week on the voice detection features."},
            {'voice': 'male2', 'text': "Absolutely. I'm the second male speaker. The voice analysis features are working much better than we initially expected."}
        ]
    },
    
    '3_female_boy_girl': {
        'description': '1 Female + 1 Boy Child + 1 Girl Child',
        'speakers': [
            {'voice': 'female1', 'text': "Hello kids, this is mom speaking. Can you both say hello to test the microphone? Let me hear your voices clearly."},
            {'voice': 'child_boy', 'text': "Hello everyone! My name is Tommy and I'm a boy. I like robots and playing video games. This is so cool!", 'pitch': '+10st'},
            {'voice': 'child_girl', 'text': "Hi everybody! I'm Sarah and I'm a girl. I love to sing songs and dance. This is really fun to test!", 'pitch': '+12st'}
        ]
    },
    
    '4_two_females': {
        'description': '2 Different Females (Duet/Conversation)',
        'speakers': [
            {'voice': 'female1', 'text': "Have you tried the new speech recognition system yet? I'm really impressed with how accurately it works. This is amazing technology."},
            {'voice': 'female2', 'text': "Yes, I have! It's amazing how accurately it detects different voices and genders. The results are much better than I expected."}
        ]
    },
    
    '5_two_males': {
        'description': '2 Different Males (Business Discussion)',
        'speakers': [
            {'voice': 'male1', 'text': "Good afternoon. The quarterly results show significant improvement in our AI models and voice detection systems. This is excellent progress."},
            {'voice': 'male2', 'text': "That's excellent news indeed. The team has done outstanding work on speaker identification. We should be very proud of these results."}
        ],
        'silence': 1.0  # Longer silence to help separation
    },
    
    '6_three_females': {
        'description': '3 Different Females (Group Chat)',
        'speakers': [
            {'voice': 'female1', 'text': "Welcome to our podcast. I'm your host, Jenny. Today we're testing voice detection technology with multiple female speakers."},
            {'voice': 'female2', 'text': "Hi everyone, Aria here. Great to be on the show today. I'm really excited to test this new voice analysis system."},
            {'voice': 'female3', 'text': "And I'm Sara, the third female speaker. Thanks for having us on the show. This is going to be a great conversation."}
        ],
        'silence': 1.2  # Even longer silence
    },
    
    '7_three_males': {
        'description': '3 Different Males (Panel Discussion)',
        'speakers': [
            {'voice': 'male1', 'text': "Let's start with the technical overview. I'm Guy, the first male speaker. We'll cover the architecture and implementation details."},
            {'voice': 'male2', 'text': "Eric here, second male speaker. I'll cover the implementation details and the specific algorithms we're using for voice detection."},
            {'voice': 'male3', 'text': "And I'm Tony, the third male speaker. I'll discuss the performance metrics and accuracy measurements we've achieved."}
        ],
        'silence': 1.2
    },
    
    '8_family_dinner': {
        'description': 'Family Dinner (Mom, Dad, 2 Kids)',
        'speakers': [
            {'voice': 'female1', 'text': "Dinner is ready everyone! Come to the table. I've made your favorite meal tonight. Let's eat together as a family."},
            {'voice': 'male1', 'text': "Smells delicious, honey. I'm really hungry. Kids, make sure you wash your hands first before sitting down."},
            {'voice': 'child_boy', 'text': "Coming, dad! I'm so hungry! Can I have extra potatoes? I washed my hands already!", 'pitch': '+10st'},
            {'voice': 'child_girl', 'text': "Me too! I'm starving! Can I please have extra dessert tonight? I've been really good all day!", 'pitch': '+12st'}
        ],
        'silence': 1.0
    },
    
    '9_interview': {
        'description': 'Job Interview (Female Interviewer + Male Candidate)',
        'speakers': [
            {'voice': 'female1', 'text': "Thank you for coming in today. I'm the hiring manager. Please tell me about your experience with artificial intelligence and voice recognition."},
            {'voice': 'male1', 'text': "Thank you for having me. I'm the candidate. I've worked on speech recognition and voice analysis systems for the past five years."},
            {'voice': 'female1', 'text': "That's very impressive. Can you describe your most challenging project and what you learned from that experience?"}
        ],
        'silence': 1.0
    },
    
    '10_meeting': {
        'description': 'Business Meeting (2M + 2F)',
        'speakers': [
            {'voice': 'male1', 'text': "Let's begin today's meeting. I'm the moderator. First item on the agenda is our quarterly review and strategic planning."},
            {'voice': 'female1', 'text': "Thank you. I'd like to discuss our Q4 targets and strategies. We need to focus on improving our voice detection accuracy."},
            {'voice': 'male2', 'text': "Good point. We should also review the budget allocations for the next quarter and ensure proper resource distribution."},
            {'voice': 'female2', 'text': "And I'll present the detailed market analysis data after that. Our competitors are also advancing quickly in this space."}
        ],
        'silence': 1.0
    },
    
    '11_overlapping_speech': {
        'description': 'Overlapping Speech Test (Fast-paced)',
        'speakers': [
            {'voice': 'male1', 'text': "Wait, let me finish my point first please. I was in the middle of explaining something important about the system."},
            {'voice': 'female1', 'text': "Sorry, I thought you were done speaking. I apologize for interrupting. Please continue with your explanation."},
            {'voice': 'male2', 'text': "Can we please take turns speaking? This is important and we need to hear everyone clearly. Let's be more organized."}
        ],
        'silence': 0.5
    },
    
    '12_accent_variety': {
        'description': 'Accent Variety (US + UK)',
        'speakers': [
            {'voice': 'female1', 'text': "Hello from the United States. Welcome to our international show. I'm your American host speaking today."},
            {'voice': 'female4', 'text': "Greetings from the United Kingdom. Lovely to be here today. I'm your British co-host with a different accent."},
            {'voice': 'male1', 'text': "And I'm joining from the West Coast of America. Great to be part of this diverse panel discussion today."},
            {'voice': 'male4', 'text': "Brilliant! I'm calling in from London, England. Wonderful to have such variety in our voices and accents today."}
        ],
        'silence': 1.0
    }
}

# -------------------------------------------------------
# Generate a WAV file using Edge TTS with optional pitch shift
# -------------------------------------------------------
async def generate_voice(text, voice, path, pitch=None):
    """Generate speech with optional pitch shifting"""
    # Add pitch parameter if specified
    prosody = f"<prosody pitch='{pitch}'>{text}</prosody>" if pitch else text
    
    communicate = edge_tts.Communicate(text=prosody, voice=VOICES[voice])
    await communicate.save(path)
    print(f"  ✓ Generated: {os.path.basename(path)}")

# -------------------------------------------------------
# Combine audio files into one dialogue
# -------------------------------------------------------
def combine_audio(files, output, silence_sec=0.8):
    """Combine multiple audio files with silence between them"""
    segments = []

    for f in files:
        audio = AudioSegment.from_file(f)
        segments.append(audio)
        # Add silence between speakers
        segments.append(AudioSegment.silent(duration=int(silence_sec * 1000)))

    # Remove last silence
    if segments:
        segments = segments[:-1]
    
    final_audio = sum(segments)
    final_audio.export(output, format="wav")
    print(f"  ✅ Combined: {os.path.basename(output)}")

# -------------------------------------------------------
# Generate a single scenario
# -------------------------------------------------------
async def generate_scenario(scenario_id, scenario_data):
    """Generate audio for a single test scenario"""
    print(f"\n📂 Generating: {scenario_id}")
    print(f"   Description: {scenario_data['description']}")
    
    temp_files = []
    
    # Generate each speaker's audio
    for i, speaker in enumerate(scenario_data['speakers']):
        temp_path = os.path.join(OUTPUT_DIR, f"{scenario_id}_speaker_{i}.wav")
        pitch = speaker.get('pitch', None)
        
        await generate_voice(
            text=speaker['text'],
            voice=speaker['voice'],
            path=temp_path,
            pitch=pitch
        )
        temp_files.append(temp_path)
    
    # Combine all speakers
    output_path = os.path.join(OUTPUT_DIR, f"{scenario_id}.wav")
    silence = scenario_data.get('silence', 0.8)
    combine_audio(temp_files, output_path, silence_sec=silence)
    
    # Cleanup temp files
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except:
            pass
    
    return output_path

# -------------------------------------------------------
# Main async runner
# -------------------------------------------------------
async def main():
    print("="*60)
    print("🎤 MULTI-SPEAKER DIALOGUE GENERATOR")
    print("="*60)
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🎯 Total scenarios: {len(SCENARIOS)}")
    
    # Generate all scenarios
    generated_files = []
    
    for scenario_id, scenario_data in SCENARIOS.items():
        output_path = await generate_scenario(scenario_id, scenario_data)
        generated_files.append((scenario_id, scenario_data['description'], output_path))
    
    # Summary
    print("\n" + "="*60)
    print("✅ GENERATION COMPLETE!")
    print("="*60)
    print("\n📋 Generated Test Files:\n")
    
    for i, (scenario_id, description, path) in enumerate(generated_files, 1):
        print(f"{i:2d}. {scenario_id}")
        print(f"    {description}")
        print(f"    📄 {path}")
        print()
    
    print("="*60)
    print("💡 Next Steps:")
    print("   1. Upload these files to Voice Analyzer")
    print("   2. Check if speaker count is detected correctly")
    print("   3. Verify gender classification for each speaker")
    print("   4. Test with different audio formats")
    print("="*60)

# -------------------------------------------------------
# Run the program
# -------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())