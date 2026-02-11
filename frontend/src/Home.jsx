import "./Home.css";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="page home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-title-block">
            <img src="/nexa-logo.png" alt="NEXA" className="hero-logo" />
            <h1 className="hero-title">NEXA</h1>
          </div>
          <p className="hero-subtitle">Your AI transfer guide for UC Computer Science</p>
          <p className="hero-description">
            Get personalized answers about course equivalencies, requirements, and transfer paths 
            between DVC and UC Berkeley, UC Davis, and UC San Diego.
          </p>
          <Link to="/chat" className="btn btn-primary btn-large">
            Start Chatting
          </Link>
        </div>
        
        {/* Gradient Orb Background */}
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <h2>What NEXA Can Help With</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3>Course Equivalencies</h3>
            <p>Find equivalent courses at your destination UC campus with detailed comparisons.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">✓</div>
            <h3>Requirements</h3>
            <p>Understand major requirements, prerequisites, and credit transfer policies.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Planning</h3>
            <p>Plan your transfer path with AI-powered recommendations tailored to you.</p>
          </div>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="stats-section">
        <div className="stat-item">
          <div className="stat-value">40+</div>
          <div className="stat-label">Course Mappings</div>
        </div>
        <div className="stat-divider"></div>
        <div className="stat-item">
          <div className="stat-value">3</div>
          <div className="stat-label">UC Campuses</div>
        </div>
        <div className="stat-divider"></div>
        <div className="stat-item">
          <div className="stat-value">24/7</div>
          <div className="stat-label">Instant Answers</div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Plan Your Transfer?</h2>
          <p>Get started with a question about courses, requirements, or transfer planning.</p>
          <div className="cta-buttons">
            <Link to="/chat" className="btn btn-primary">
              Open Chat
            </Link>
            <Link to="/how-to" className="btn btn-secondary">
              Learn More
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
