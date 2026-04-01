# AI Enhancer Setup Guide

## Overview

PhotoEnhancer now integrates with two powerful AI services:

1. **Remove.bg** - Remove or replace backgrounds automatically
2. **Deep-image.ai** - Enhance photo quality, upscale, colorize, and more

## Quick Start

### Step 1: Get Your API Keys

#### Remove.bg API Key
1. Visit https://www.remove.bg/
2. Sign up for an account (free tier available: 50 credits)
3. Go to https://www.remove.bg/api
4. Copy your API key

#### Deep-image.ai API Key
1. Visit https://deep-image.ai/
2. Sign up for an account (free tier: 50 credits/month)
3. Go to https://deep-image.ai/my-account/api-keys
4. Create a new API key

### Step 2: Configure API Keys

Choose one of the following methods:

#### Option A: Environment Variables (Recommended for Production)

Add to your `.env` file:

```env
# Remove.bg Configuration
REMOVE_BG_API_KEY=your-actual-remove-api-key-here

# Deep-image.ai Configuration
DEEP_IMAGE_API_KEY=your-actual-deep-image-api-key-here
```

#### Option B: settings.py (For Development)

Edit `Backend/photo_enhancer/settings.py`:

```python
# AI Enhancer API Configuration
REMOVE_BG_API_KEY = 'your-actual-remove-api-key-here'
DEEP_IMAGE_API_KEY = 'your-actual-deep-image-api-key-here'
```

### Step 3: Restart Server

```bash
# Stop current server (Ctrl+C)
# Restart

python manage.py runserver
```

### Step 4: Verify Setup

Check if services are configured:

```bash
curl http://localhost:8000/api/ai-services/status/
```

You should see:
```json
{
  "services": {
    "remove_bg": true,
    "deep_image": true
  },
  "configured": true,
  "issues": null,
  "message": "All services ready"
}
```

## API Usage

### Upload Photo with AI Enhancement

```bash
curl -X POST http://localhost:8000/api/photos/upload/ \
  -H "X-CSRFToken: your-token" \
  -H "Cookie: sessionid=your-session" \
  -F "photo=@/path/to/your/image.jpg" \
  -F 'settings={"type":"enhance","preset":"enhance"}'
```

### Enhancement Types

| Type | Description | Required API |
|------|-------------|--------------|
| `enhance` | AI photo enhancement (quality, upscale) | Deep-image.ai |
| `remove_bg` | Remove/replace background | Remove.bg |
| `both` | Remove BG then enhance | Both APIs |

### Deep-image.ai Presets

| Preset | Description |
|--------|-------------|
| `enhance` | General enhancement |
| `colorize` | Colorize black & white |
| `denoise` | Remove noise |
| `upscale_2x` | 2x upscaling |
| `upscale_4x` | 4x upscaling (Pro tier+) |
| `upscale_8x` | 8x upscaling (Enterprise tier) |
| `hdr` | HDR effect |
| `portrait` | Portrait enhancement |
| `night` | Night photo enhancement |
| `color_enhance` | Color enhancement |
| `sharp_enhance` | Sharpness enhancement |

## Get Enhancement Options

```bash
curl http://localhost:8000/api/ai-services/options/ \
  -H "Cookie: sessionid=your-session"
```

Returns available options based on your subscription tier.

## Pricing Tiers & Limits

### Free Tier
- **Remove.bg**: 50 credits (1 image = 1 credit)
- **Deep-image.ai**: 50 credits/month
- **Our App**: 5 photos/month

### Pro Tier ($9/month)
- **Our App**: Unlimited photos
- Deep-image: Up to 4K upscaling
- Priority processing

### Enterprise Tier ($49/month)
- **Our App**: Unlimited photos + API access
- Deep-image: Up to 8K upscaling
- Custom training options
- Team collaboration

## Fallback Mode

If no API keys are configured, the app will use a **fallback mode** with Pillow (PIL) for basic enhancements:
- Brightness adjustment
- Contrast enhancement
- Sharpening
- Basic denoising
- Upscaling (nearest-neighbor, lower quality)

## Troubleshooting

### "API not configured" Error
```
Add your API keys to settings.py or .env file
```

### "Insufficient credits" Error
```
Check your API provider dashboard:
- Remove.bg: https://www.remove.bg/profile
- Deep-image: https://deep-image.ai/my-account/credits
```

### API Timeout
```
Images are processed asynchronously. Check status with:
GET /api/photos/<uuid>/
```

### Check Service Status
```bash
curl http://localhost:8000/api/ai-services/status/
```

## API Response Examples

### Upload Response
```json
{
  "message": "Photo uploaded successfully. Processing started.",
  "photo": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "original_url": "http://localhost:8000/media/uploads/1/550e8400-e29b-41d4-a716-446655440000.jpg",
    "created_at": "2024-01-15T10:30:00+00:00",
    "task_id": "abc123-456def-789"
  }
}
```

### Check Processing Status
```bash
curl http://localhost:8000/api/photos/550e8400-e29b-41d4-a716-446655440000/
```

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "enhancement_settings": {
    "type": "enhance",
    "preset": "upscale_2x"
  },
  "enhanced": {
    "url": "http://localhost:8000/media/enhanced/1/enhanced_550e8400-e29b-41d4-a716-446655440000.jpg",
    "width": 1920,
    "height": 1080
  }
}
```

## Support

- **Remove.bg**: https://www.remove.bg/contact
- **Deep-image.ai**: support@deep-image.ai
- **Our Docs**: See DEPLOYMENT.md for full setup
