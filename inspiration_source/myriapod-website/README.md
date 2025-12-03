# Myriapod Robot Research Website

A modern, technical website showcasing the bio-inspired myriapod robot research project from Arizona State University's RAS 557: Foldable Robotics course.

## 🚀 Deploying to GitHub Pages

### Quick Setup

1. **Create a new GitHub repository**
   - Go to [GitHub](https://github.com) and create a new repository
   - Name it something like `myriapod-robot` (or any name you prefer)
   - Keep it public (required for free GitHub Pages)

2. **Upload your files**
   - Upload all files from the `myriapod-website` folder to your repository:
     - `index.html`
     - `styles.css`
     - `script.js`
     - `images/` folder (with all images)

3. **Enable GitHub Pages**
   - Go to your repository Settings
   - Scroll down to "Pages" in the left sidebar
   - Under "Source", select "Deploy from a branch"
   - Select `main` branch and `/ (root)` folder
   - Click "Save"

4. **Access your website**
   - After a few minutes, your site will be live at:
   - `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

### Alternative: Using Git Command Line

```bash
# Initialize git repository
cd myriapod-website
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Myriapod robot website"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

Then follow step 3 above to enable GitHub Pages.

## 🎨 Design Features

- **Distinctive Dark Theme**: Technical aesthetic with cyan/teal accents
- **Custom Typography**: JetBrains Mono and Crimson Pro fonts
- **Smooth Animations**: Scroll-triggered fade-in effects and parallax
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modular Sections**: Easy navigation with smooth scrolling
- **Scientific Layout**: Optimized for technical content presentation

## 📁 File Structure

```
myriapod-website/
├── index.html          # Main HTML file
├── styles.css          # All styling
├── script.js           # Interactive features
├── images/             # All research images
│   ├── fig_concept.png
│   ├── fig_gait.jpg
│   ├── fig_kinematics.png
│   ├── fig_prototype.png
│   ├── fig_spine.png
│   ├── leg_design.jpg
│   ├── leg_design_1.jpg
│   ├── leg_scrap.jpg
│   ├── spine_prototype_1.jpg
│   └── spine_prototype_1_scraps.jpg
└── README.md           # This file
```

## 🔧 Customization

### Changing Colors

Edit the CSS variables in `styles.css`:

```css
:root {
    --accent-primary: #00d9ff;     /* Main accent color */
    --accent-secondary: #00ffc8;   /* Secondary accent */
    --bg-primary: #0a0e14;         /* Background color */
}
```

### Adding Sections

Add new sections in `index.html` following the existing pattern:

```html
<section id="new-section" class="section">
    <div class="container">
        <div class="section-header">
            <span class="section-number">07</span>
            <h2 class="section-title">New Section Title</h2>
        </div>
        <!-- Your content here -->
    </div>
</section>
```

Don't forget to add the corresponding navigation link in the navbar!

### Optimizing Images

For faster loading, you can compress images using tools like:
- [TinyPNG](https://tinypng.com/)
- [Squoosh](https://squoosh.app/)
- ImageOptim (Mac)

## 📱 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📝 License

This website is created for academic purposes. Please credit the research team when using or adapting this design.

## 👥 Research Team

- Jeevan Hebbal Manjunath
- Varun Karthik
- Yeshwanth Reddy Gurreddy

Arizona State University · RAS 557: Foldable Robotics · October 2025

---

**Note**: This is a static website with no backend requirements. It's optimized for GitHub Pages hosting and requires no additional setup or dependencies.
