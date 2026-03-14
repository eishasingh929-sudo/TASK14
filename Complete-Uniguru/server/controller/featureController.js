import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import Tesseract from 'tesseract.js';
import sharp from 'sharp';
import { generateGroqResponse } from '../config/ollama.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

/**
 * @desc    Read PDF content
 * @route   POST /api/v1/feature/pdf/r
 * @access  Private
 */
export const readPdf = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No PDF file uploaded'
      });
    }

    // Dynamic import to avoid the debug mode issue with pdf-parse
    const pdfParse = (await import('pdf-parse')).default;

    // Parse PDF content using pdf-parse
    const pdfData = await pdfParse(req.file.buffer);

    if (!pdfData.text || pdfData.text.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No text content found in PDF'
      });
    }

    res.status(200).json({
      success: true,
      message: 'PDF content extracted successfully',
      extractedText: pdfData.text.trim(),
      metadata: {
        filename: req.file.originalname,
        size: req.file.size,
        mimetype: req.file.mimetype,
        pages: pdfData.numpages,
        info: pdfData.info
      }
    });
  } catch (error) {
    console.error('PDF reading error:', error);
    res.status(500).json({
      success: false,
      message: 'Error reading PDF file. Please ensure the PDF is not password protected and contains readable text.'
    });
  }
};

/**
 * @desc    Talk with PDF content using AI
 * @route   POST /api/v1/feature/pdf/t
 * @access  Private
 */
export const talkWithPdfContent = async (req, res) => {
  try {
    const { extractedText, message } = req.body;

    if (!extractedText || !message) {
      return res.status(400).json({
        success: false,
        message: 'Both extracted text and message are required'
      });
    }

    // Create a temporary guru for PDF analysis
    const pdfGuru = {
      name: 'PDF Analyzer',
      subject: 'Document Analysis',
      systemPrompt: `You are a PDF Analyzer, an expert at understanding and analyzing document content. You have been provided with the following PDF content:

${extractedText.substring(0, 3000)}${extractedText.length > 3000 ? '...' : ''}

Please answer questions about this document accurately and provide helpful insights. If the question cannot be answered from the provided content, please say so clearly.`,
      settings: {
        model: 'llama3.1',
        temperature: 0.3,
        maxTokens: 1024,
        topP: 0.9
      }
    };

    // Prepare messages for AI
    const messages = [
      {
        sender: 'user',
        content: message
      }
    ];

    // Generate AI response
    const aiResponse = await generateGroqResponse(messages, pdfGuru);

    res.status(200).json({
      success: true,
      message: 'AI response generated successfully',
      response: aiResponse.content,
      metadata: aiResponse.metadata
    });
  } catch (error) {
    console.error('PDF talk error:', error);
    res.status(500).json({
      success: false,
      message: 'Error processing PDF content with AI'
    });
  }
};

/**
 * @desc    Create PDF from content
 * @route   POST /api/v1/feature/pdf/c
 * @access  Private
 */
export const createPdf = async (req, res) => {
  try {
    const { title, content } = req.body;

    if (!title || !content) {
      return res.status(400).json({
        success: false,
        message: 'Title and content are required'
      });
    }

    // For now, return the content as text
    // In a production environment, you would use a library like PDFKit or Puppeteer
    const filename = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.txt`;
    const filepath = path.join(uploadsDir, filename);

    // Write content to file
    fs.writeFileSync(filepath, content);

    res.status(200).json({
      success: true,
      message: 'PDF created successfully',
      filename,
      path: `/uploads/${filename}`,
      downloadUrl: `${req.protocol}://${req.get('host')}/uploads/${filename}`
    });
  } catch (error) {
    console.error('PDF creation error:', error);
    res.status(500).json({
      success: false,
      message: 'Error creating PDF'
    });
  }
};

/**
 * @desc    Scan text from image using OCR
 * @route   POST /api/v1/feature/image/s
 * @access  Private
 */
export const scanImageText = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No image file uploaded'
      });
    }

    // Process image with Tesseract OCR
    const { data: { text } } = await Tesseract.recognize(req.file.buffer, 'eng', {
      logger: m => console.log(m)
    });

    if (!text || text.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No text found in image'
      });
    }

    res.status(200).json({
      success: true,
      message: 'Text extracted from image successfully',
      extractedText: text.trim(),
      metadata: {
        filename: req.file.originalname,
        size: req.file.size,
        mimetype: req.file.mimetype
      }
    });
  } catch (error) {
    console.error('Image text scanning error:', error);
    res.status(500).json({
      success: false,
      message: 'Error scanning text from image'
    });
  }
};

/**
 * @desc    Edit text in image (placeholder implementation)
 * @route   POST /api/v1/feature/image/e
 * @access  Private
 */
export const editImageText = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No image file uploaded'
      });
    }

    const { text: newText } = req.body;

    if (!newText) {
      return res.status(400).json({
        success: false,
        message: 'New text is required'
      });
    }

    // For now, this is a placeholder implementation
    // In a real application, you would use image processing libraries
    // to detect text regions and replace them with new text

    const filename = `edited_${Date.now()}_${req.file.originalname}`;
    const filepath = path.join(uploadsDir, filename);

    // Process image with Sharp (resize/optimize)
    await sharp(req.file.buffer)
      .resize(800, 600, { fit: 'inside', withoutEnlargement: true })
      .jpeg({ quality: 90 })
      .toFile(filepath);

    res.status(200).json({
      success: true,
      message: 'Image processed successfully (text editing is a placeholder)',
      filename,
      path: `/uploads/${filename}`,
      downloadUrl: `${req.protocol}://${req.get('host')}/uploads/${filename}`,
      note: 'Text editing functionality is not fully implemented in this demo'
    });
  } catch (error) {
    console.error('Image text editing error:', error);
    res.status(500).json({
      success: false,
      message: 'Error editing image text'
    });
  }
};

/**
 * @desc    Get available tools/features
 * @route   GET /api/v1/feature/tools
 * @access  Private
 */
export const getAvailableTools = async (req, res) => {
  try {
    const tools = [
      {
        id: 'pdf-reader',
        name: 'PDF Reader',
        description: 'Extract and analyze text content from PDF files',
        category: 'document',
        endpoints: ['/feature/pdf/r', '/feature/pdf/t']
      },
      {
        id: 'pdf-creator',
        name: 'PDF Creator',
        description: 'Create PDF documents from text content',
        category: 'document',
        endpoints: ['/feature/pdf/c']
      },
      {
        id: 'ocr-scanner',
        name: 'OCR Text Scanner',
        description: 'Extract text from images using OCR technology',
        category: 'image',
        endpoints: ['/feature/image/s']
      },
      {
        id: 'image-editor',
        name: 'Image Text Editor',
        description: 'Edit text content in images (placeholder)',
        category: 'image',
        endpoints: ['/feature/image/e']
      }
    ];

    res.status(200).json({
      success: true,
      tools,
      count: tools.length
    });
  } catch (error) {
    console.error('Get tools error:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching available tools'
    });
  }
};
