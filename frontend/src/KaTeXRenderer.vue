<template>
    <div ref="mathContainer">{{ content }}</div>
  </template>
  
  <script>
  import "katex/dist/katex.min.css";
  import renderMathInElement from "katex/contrib/auto-render";
  
  export default {
    props: {
      content: {
        type: String,
        required: true, // The content includes plain text and LaTeX math
      },
    },
    mounted() {
      this.renderMath();
    },
    updated() {
      this.renderMath(); // Ensure re-rendering on content update
    },
    methods: {
      renderMath() {
        try {
          renderMathInElement(this.$refs.mathContainer, {
            delimiters: [
              { left: "$$", right: "$$", display: true },
              { left: "$", right: "$", display: false },
              { left: "\\(", right: "\\)", display: false },
              { left: "\\[", right: "\\]", display: true },
            ],
            throwOnError: false,
          });
        } catch (error) {
          console.error("KaTeX auto-rendering error:", error);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  /* Scoped styles if necessary */
  </style>
  