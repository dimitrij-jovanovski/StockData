import React, { useState, useEffect } from "react";
import axios from "axios"; // Assuming you're using Axios for API calls
import { useNavigate } from "react-router-dom"; // React Router for navigation

// Inline styles to maintain the same appearance
const searchPageStyles = {
  container: {
    width: "70%",
    textAlign: "left",
  },
  title: {
    fontSize: "3rem",
    letterSpacing: "0.1em",
    textAlign: "center",
  },
  subtitle: {
    fontSize: "1.2rem",
    marginTop: "10px",
    letterSpacing: "0.05em",
    textAlign: "center",
  },
  searchContainer: {
    display: "flex",
    alignItems: "center",
    margin: "30px 0",
    borderBottom: "2px solid #0ac4ff",
    paddingBottom: "10px",
  },
  input: {
    flex: 1,
    padding: "10px",
    fontSize: "1rem",
    color: "#0ac4ff",
    background: "transparent",
    border: "none",
    outline: "none",
    caretColor: "#0ac4ff",
  },
  searchIcon: {
    fontSize: "1.5rem",
    color: "#0ac4ff",
    marginRight: "10px",
  },
  list: {
    marginTop: "20px",
  },
  listItem: {
    marginBottom: "20px",
  },
  listLink: {
    color: "#0ac4ff",
    textDecoration: "none",
    fontSize: "1.2rem",
    transition: "color 0.3s ease",
  },
  listLinkHover: {
    color: "#67e3ff",
  },
  backgroundEffect: {
    position: "absolute",
    top: "0",
    left: "0",
    width: "100%",
    height: "100%",
    background: "radial-gradient(circle, rgba(58,123,213,0.3) 0%, rgba(0,0,0,0) 60%)",
    zIndex: "-1",
  },
};

const SearchStocks = () => {
  const [searchTerm, setSearchTerm] = useState(""); // State for search input
  const [stockList, setStockList] = useState([]); // State for list of stocks
  const navigate = useNavigate(); // For navigation

  // Function to handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  // Fetch stocks based on search term (currently only ADIN)
  const fetchStocks = async () => {
    if (searchTerm.toUpperCase() === "ADIN") {
      setStockList([
        { id: 1, issuer_code: "ADIN", name: "Адитус" },
      ]);
    } else {
      setStockList([]); // Clear results if no match
    }
  };

  // Use useEffect to trigger the search whenever the search term changes
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchStocks();
    }, 500); // Wait 500ms after the user stops typing to trigger the search

    return () => clearTimeout(timeoutId); // Cleanup timeout on unmount
  }, [searchTerm]);

  // Redirect to the info page for the selected stock
  const handleStockClick = (stock) => {
    navigate(`/info/${stock.issuer_code}`); // Assuming you're using React Router for routing
  };

  return (
      <div style={searchPageStyles.container}>
        <h1 style={searchPageStyles.title}>Search Stocks</h1>
        <p style={searchPageStyles.subtitle}>Find the Issuer Code</p>
        <div style={searchPageStyles.searchContainer}>
          <span style={searchPageStyles.searchIcon}>🔍</span>
          <input
              type="text"
              placeholder="Enter issuer code..."
              value={searchTerm}
              onChange={handleSearchChange}
              style={searchPageStyles.input}
          />
        </div>

        <div style={searchPageStyles.list}>
          {stockList.length > 0 ? (
              stockList.map((stock) => (
                  <div key={stock.id} style={searchPageStyles.listItem}>
                    <a
                        href="../../..#"
                        onClick={() => handleStockClick(stock)} // Navigate to info page
                        style={searchPageStyles.listLink}
                    >
                      {stock.issuer_code} - {stock.name}
                    </a>
                  </div>
              ))
          ) : (
              <p style={searchPageStyles.subtitle}>No stocks found</p>
          )}
        </div>

        <div style={searchPageStyles.backgroundEffect}></div>
      </div>
  );
};

export default SearchStocks;
